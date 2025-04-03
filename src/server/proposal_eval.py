from collections import defaultdict
from src.models.tot_agent import SimpleToTAgent, TreeNode, generate_thoughts_openai, score_thought_with_openai
from src.server.react_agent import ReActConsultantAgent, run_react_loop_for_rfp_eval, run_missing_relevant_tools
from src.models.llmscoring_rfp import score_proposal_content_with_llm_and_tools
from src.utils.tools.tool_embeddings import build_tool_embeddings
from src.models.openai_interface import call_openai_with_tracking
from src.utils.tools.tool_catalog_RFP import tool_catalog
from src.utils.tools.tool_dispatch import TOOL_FUNCTION_MAP
import uuid
from src.utils.file_loader import preprocess_proposal_for_criteria_with_threshold
from src.utils.logging_utils import log_phase, log_result, print_tool_stats
import json
from src.utils.tools.tool_analysis import get_relevant_tools
from src.utils.tools.tools_general import extract_tool_name
from src.utils.thought_filtering import reset_embedding_cache

def evaluate_proposal(proposal_text, rfp_criteria, model="gpt-3.5-turbo", executed_tools_global=None):
    executed_tools_global = executed_tools_global
    reset_embedding_cache()  # Clear cache at the beginning of each evaluation

    matched_sections = preprocess_proposal_for_criteria_with_threshold(
        proposal_text=proposal_text,
        rfp_criteria=rfp_criteria,
        score_threshold=0.4
    )
    log_phase("✅ Proposal preprocessed = parse content by criteria.")

    results = []
    seen_thoughts = []
    seen_embeddings = []

    for criterion_dict in rfp_criteria:
        criterion = criterion_dict["name"]
        section_text = matched_sections.get(criterion, "")
        log_phase(f"\n📌 Evaluating criterion: {criterion}")

        result = evaluate_single_criterion(
            criterion=criterion,
            section_text=section_text,
            proposal_text=proposal_text,
            model=model,
            seen_thoughts=seen_thoughts,
            seen_embeddings=seen_embeddings,
            executed_tools_global=executed_tools_global
        )

        results.append(result)

    overall_score = round(sum(r["proposal_score"] for r in results) / len(results), 2)
    log_phase(f"\n✅ Overall score: {overall_score}/10")

    eval_summary = ''.join(
        f"- {r['criterion']}: Score {r['proposal_score']}/10 – {r['proposal_explanation']}\n"
        for r in results
    )

    swot_prompt = f"""
You are summarizing a vendor proposal based on the following criterion-level evaluations:

{eval_summary}

Generate a SWOT assessment (Strengths, Weaknesses, Opportunities, Threats) for this proposal.
"""
    messages = [{"role": "user", "content": swot_prompt}]
    swot_summary = call_openai_with_tracking(messages, model=model)

    return results, overall_score, swot_summary


def evaluate_single_criterion(criterion, section_text, proposal_text, model, seen_thoughts, seen_embeddings, executed_tools_global):
    # Your current block of logic for evaluating a single criterion goes here
    # Including: ToT, ReAct, auto tools, scoring, reasoning trace, etc.

    # Return a result dict with all relevant info for this criterion

    # Step 1: Run ToT for reasoning path to generate thoughts (questions) by criterion
    tot_agent = SimpleToTAgent(
        llm=generate_thoughts_openai,
        scorer=lambda t: score_thought_with_openai(t, criterion, section_text),
        beam_width=1,
        max_depth=2
    )
    result = tot_agent.run(section=section_text, criterion=criterion, seen_thoughts=seen_thoughts, seen_embeddings=seen_embeddings)
    top_thoughts = result["reasoning_path"]
    thought_records= [  # keep track of thoughts for analysis
        {
            "text": t,
            "source": "ToT",
            "used_in_tool": False,
            "used_in_scoring": True  # All thoughts go to scoring prompt
        }
        for t in top_thoughts
    ]

    # Step 2–4: Run ReAct loop using ToT thoughts and embedding-aware tool selection
    react_agent = ReActConsultantAgent(section_name=criterion, section_text=section_text, proposal_text=proposal_text)
    report_sections = {"Proposal": proposal_text}
    tool_embeddings = build_tool_embeddings(tool_catalog)
    log_phase(f"Running ReAct loop for criterion '{criterion}' with tool embeddings.")
    tool_history = run_react_loop_for_rfp_eval(
        agent=react_agent,
        criterion=criterion,
        section_text=section_text,
        full_proposal_text=proposal_text,
        thoughts=top_thoughts,
        tool_embeddings=tool_embeddings,
        report_sections=report_sections,
        max_steps=2,
        seen_thoughts=seen_thoughts,
        seen_embeddings=seen_embeddings,
        executed_tools_global=executed_tools_global
    )

    # Step 5: Extract ReAct Thought->Act->Observe history for context in proposal evaluation
    triggered_tools = [
        {
            "tool": step["action"],
            "result": step["observation"],
            "thought": step["thought"]
        }
        for step in tool_history
        if step.get("action") not in ["summarize", "ask_question", "tool_help", "suggest_tool_for", "highlight_missing_sections", "compare_with_other_sections"] and step.get("observation")
    ]
    result["react_thoughts"] = [step["thought"] for step in tool_history]
    thought_records.extend([  # keep track of thoughts for analysis
        {
            "text": step["thought"],
            "source": "ReAct",
            "used_in_tool": step["action"] not in ["summarize", "ask_question", "tool_help"],  # heuristic
            "used_in_scoring": True  # still included in LLM score prompt
        }
        for step in tool_history
    ])
    
    # Combine ToT and ReAct thoughts
    all_thoughts = top_thoughts + result["react_thoughts"]
    result["all_thoughts"] = [t["text"] for t in thought_records]  # for compatibility
    result["thought_records"] = thought_records
    if not all_thoughts:
        log_phase("⚠️ No usable thoughts available for scoring.")

    # Check for relevant tools that have been missed
    relevant_tools = get_relevant_tools(criterion, section_text, tool_embeddings)
    tools_used = [extract_tool_name(t["tool"]) for t in triggered_tools]
    missing_tools = []
    for tool in relevant_tools:
        if isinstance(tool, tuple):  # (tool_name, score) format
            tool_name, score = tool
        else:  # tool_name only
            tool_name, score = tool, None
        if tool_name not in tools_used:
            missing_tools.append((tool_name, score))
    log_phase(f"Missing tools for criterion '{criterion}': {json.dumps(missing_tools, indent=2)}")

    # === Auto-run missing relevant tools ===
    auto_tool_results, auto_tool_meta = run_missing_relevant_tools(
        agent=react_agent,
        criterion=criterion,
        section_text=section_text,
        relevant_tools=relevant_tools,
        tool_embeddings=tool_embeddings,
        triggered_tools=triggered_tools,
        tool_function_map=TOOL_FUNCTION_MAP,
        executed_tools_global=executed_tools_global,
        similarity_threshold=0.75,    # relevant
        run_score_threshold=0.75,    # worth running
        verbose=False
    )
    triggered_tools.extend(auto_tool_results)
    log_phase(f"Auto-triggered tools for criterion '{criterion}': {json.dumps(auto_tool_results, indent=2)}")


    # Step 6: Score proposal using LLM with ToT thoughts and tool results
    proposal_score, explanation = score_proposal_content_with_llm_and_tools(
        proposal=proposal_text,
        criterion=criterion,
        top_thoughts=all_thoughts,
        triggered_tools=triggered_tools,
        model=model
    )

    # ---- Track reasoning lineage per criterion ----
    reasoning_trace = {
        "criterion": criterion,
        "section_text": section_text,
        "tot_thoughts": [{"text": t, "score": score_thought_with_openai(t, criterion, section_text), "used_in_score": t in all_thoughts} for t in top_thoughts],
        "react_steps": [
            {
                "step": i + 1,
                "thought": step["thought"],
                "action": step["action"],
                "observation": step["observation"],
                "used_in_score": step["thought"] in all_thoughts,
                "tool_succeeded": "⚠️" not in step["observation"]  # crude check for now
            }
            for i, step in enumerate(tool_history)
        ],
        "score": proposal_score,
        "score_explanation": explanation,
        "tools_used": tools_used,
        "missing_tools": missing_tools,
        "auto_tools_meta": auto_tool_meta
    }

    # Group missing tools by section
    reasoning_trace["missing_tools_by_section"] = defaultdict(list)
    for tool_name, score in missing_tools:
        section = tool_catalog.get(tool_name, {}).get("section", "Unknown")
        reasoning_trace["missing_tools_by_section"][section].append((tool_name, score))
    log_phase(f"Missing tools for criterion '{criterion}': {json.dumps(reasoning_trace['missing_tools_by_section'], indent=2)}")

    log_phase(f"Reasoning trace for criterion '{criterion}': {json.dumps(reasoning_trace, indent=2)}")
    
    # Combine manually and auto-triggered tool results
    all_triggered_tools = triggered_tools + auto_tool_results
    result["triggered_tools"] = all_triggered_tools
    reasoning_trace["missing_tools"] = missing_tools
    reasoning_trace["auto_tools_results"] = auto_tool_results

    # Step 5: Add everything to result object
    result["proposal_score"] = proposal_score
    result["proposal_explanation"] = explanation
    result["reasoning_trace"] = reasoning_trace
    
    return result