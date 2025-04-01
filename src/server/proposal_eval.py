from src.models.tot_agent import SimpleToTAgent, TreeNode, generate_thoughts_openai, score_thought_with_openai
from src.server.react_agent import ReActConsultantAgent, run_react_loop_for_rfp_eval
from src.models.llmscoring_rfp import score_proposal_content_with_llm_and_tools
from src.utils.tools.tool_embeddings import build_tool_embeddings
from src.models.openai_interface import call_openai_with_tracking
from src.utils.tools.tool_catalog_RFP import tool_catalog
import uuid
from src.utils.file_loader import preprocess_proposal_for_criteria_with_threshold
from src.utils.logging_utils import log_phase, log_result, print_tool_stats
import json

def evaluate_proposal(proposal_text, rfp_criteria, model="gpt-3.5-turbo"):
    """
    Purpose:
    Performs a full hybrid evaluation for a single proposal across all criteria. 
    Combines Tree of Thought (ToT) reasoning, ReAct tool-based analysis, proposal scoring, 
    overall score computation, and SWOT assessment generation.

    Parameters:
    - proposal_text (str): The text of the vendor proposal being evaluated.
    - rfp_criteria (list of str): A list of evaluation criteria to assess the proposal against.
    - model (str): The name of the OpenAI model to use for LLM-based reasoning and scoring. Default is "gpt-3.5-turbo".

    Workflow:
    1. Initializes an empty list to store evaluation results.
    2. Iterates through each criterion in `rfp_criteria`:
        - Runs a Tree of Thought (ToT) reasoning process to generate thoughts and reasoning paths.
        - Executes a ReAct reasoning loop to select and apply tools for analysis.
        - Scores the proposal based on the generated thoughts and tool results using an LLM.
        - Collects the criterion-level score, explanation, and tool usage into the results.
    3. Computes the overall score as a simple average of all criterion-level scores.
    4. Generates an evaluation summary string based on the results.
    5. Creates a SWOT assessment (Strengths, Weaknesses, Opportunities, Threats) using an LLM.
    6. Returns the evaluation results, overall score, and SWOT summary.

    Returns:
    - tuple: A tuple containing:
        - results (list of dict): Criterion-level evaluation results, including scores, reasoning paths, and tool usage.
        - overall_score (float): The overall average score across all criteria.
        - swot_summary (str): A SWOT assessment of the proposal.
    """
    
    matched_sections = preprocess_proposal_for_criteria_with_threshold(
        proposal_text=proposal_text,
        rfp_criteria=rfp_criteria,
        score_threshold=0.4  # you can tune this
    )
    log_phase("✅ Proposal preprocessed = parse content by criteria.")

    results = []

    for criterion in rfp_criteria:
        log_phase(f"Evaluating criterion (json): {criterion}")
        criterion = criterion["name"]
        log_phase(f"Evaluating criterion (name): {criterion}")
        section_text = matched_sections.get(criterion, "")

        # Step 1: Run ToT for reasoning path to generate thoughts (questions) by criterion
        tot_agent = SimpleToTAgent(
            llm=generate_thoughts_openai,
            scorer=lambda t: score_thought_with_openai(t, criterion, section_text),
            beam_width=1,
            max_depth=2
        )
        result = tot_agent.run(section=section_text, criterion=criterion)
        top_thoughts = result["reasoning_path"]

        # Step 2–4: Run ReAct loop using ToT thoughts and embedding-aware tool selection
        react_agent = ReActConsultantAgent(section_name=criterion, section_text=section_text, proposal_text=proposal_text)
        report_sections = {"Proposal": proposal_text}
        tool_embeddings = build_tool_embeddings(tool_catalog)
        #react_agent.report_section = proposal_text
        tool_history = run_react_loop_for_rfp_eval(
            agent=react_agent,
            criterion=criterion,
            section_text=section_text,
            full_proposal_text=proposal_text,
            thoughts=top_thoughts,
            tool_embeddings=tool_embeddings,
            report_sections=report_sections,
            max_steps=2
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
        
        # Combine ToT and ReAct thoughts
        all_thoughts = top_thoughts + result["react_thoughts"]
        result["all_thoughts"] = all_thoughts

        # Step 6: Score proposal using LLM with ToT thoughts and tool results
        proposal_score, explanation = score_proposal_content_with_llm_and_tools(
            proposal=proposal_text,
            criterion=criterion,
            top_thoughts=all_thoughts,
            triggered_tools=triggered_tools,
            model=model
        )

        # Step 5: Add everything to result object
        result["proposal_score"] = proposal_score
        result["proposal_explanation"] = explanation
        result["triggered_tools"] = triggered_tools
        results.append(result)

    # Step 6: Compute overall weighted average score (simple average for now)
    total = sum(r["proposal_score"] for r in results)
    overall_score = round(total / len(results), 2)

    # Generate the evaluation summary 
    eval_summary = ''.join(
        f"- {r['criterion']}: Score {r['proposal_score']}/10 – {r['proposal_explanation']}\n"
        for r in results
    )

    # Step 7: Generate SWOT summary using LLM
    swot_prompt = f"""
You are summarizing a vendor proposal based on the following criterion-level evaluations:

{eval_summary}

Generate a SWOT assessment (Strengths, Weaknesses, Opportunities, Threats) for this proposal.
"""
    messages = [{"role": "user", "content": swot_prompt}]
    swot_summary = call_openai_with_tracking(messages, model=model)

    log_phase("✅ Proposal evaluation complete.")
    log_phase(json.dumps(results, indent=2))  # Print entire structured result (nicely formatted)
    return results, overall_score, swot_summary
