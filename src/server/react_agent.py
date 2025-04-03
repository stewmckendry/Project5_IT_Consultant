# react_agent.py - Core class + reasoning loops

import re
from src.models.openai_interface import call_openai_with_tracking
from src.models.section_tools_llm import auto_fill_gaps_with_research, check_recommendation_alignment, check_summary_support, evaluate_smart_goals, generate_final_summary, should_cite, upgrade_section_with_research
from src.server.prompt_builders import build_tool_hints, format_tool_catalog_for_prompt
from src.models.scoring import summarize_and_score_section
from src.utils.tools.tool_catalog_RFP import tool_catalog
from src.utils.tools.tools_basic import check_guideline_dynamic, generate_client_questions, keyword_match_in_section, search_report
#from src.utils.tools.tools_basic import check_timeline_feasibility
from src.utils.tools.tools_nlp import analyze_tone_textblob, check_for_jargon, check_readability, extract_named_entities
from src.utils.tools.tools_reasoning import analyze_math_question, pick_tool_by_intent_fuzzy
from src.utils.tools.tools_web import search_arxiv, search_serpapi, search_web, search_wikipedia, should_search_arxiv
from src.server.prompt_builders import build_tool_selection_prompt_rfpeval
from src.utils.tools.tool_embeddings import suggest_tools_by_embedding
from src.models.openai_embeddings import get_openai_embedding  # used internally by suggest_tools...
#from src.utils.text_processing import truncate_text  # Optional
from src.utils.tools.tool_hints import build_tool_hints_for_rfp_eval_embedding, build_tool_hint_text_forRFPeval  # new helper
from src.utils.tools.tools_general import (
    detect_boilerplate_or_marketing_fluff,
    evaluate_writing_clarity,
    check_fact_substantiation,
    check_for_unsupported_assumptions
)
from src.utils.tools.tools_rfp_method import (
    evaluate_collaboration_approach,
)
from src.utils.tools.tools_RFP_team import (
    check_team_experience_alignment,
    detect_bait_and_switch_risk,
    check_local_resource_presence
)
from src.utils.tools.tools_rfp_experience import (
    check_vendor_experience_relevance,
    check_vendor_experience_evidence
)
from src.utils.tools.tools_RFP_plan import (
    check_implementation_milestones,
    check_resource_plan_realism,
    check_assumption_reasonableness,
    check_timeline_feasibility,
    check_contingency_plans
)
from src.utils.tools.tools_rfp_method import (
    check_discovery_approach,
    check_requirements_approach,
    check_design_approach,
    check_build_approach,
    check_test_approach,
    check_deployment_approach,
    check_operate_approach,
    check_agile_compatibility,
    check_accelerators_and_tools
)  
from src.utils.tools.tools_RFP_costs import (
    check_value_for_money,
    check_cost_benchmark,
    generate_cost_forecast
)
from src.utils.tools.tools_RFP_risk import (
    check_data_privacy_and_security_measures,
    check_risk_register_or_mitigation_plan,
    check_compliance_certifications
)
from src.utils.tools.tools_RFP_fit import (
    evaluate_product_fit,
    evaluate_nfr_support,
    evaluate_modularity_and_scalability,
    check_product_roadmap,
    evaluate_demos_and_proofs
)

from src.utils.tools.tool_dispatch import TOOL_FUNCTION_MAP
from src.utils.logging_utils import (
    log_phase, 
    log_tool_used, 
    log_tool_execution, 
    log_tool_failed,
    log_deduplication
)
import time
from src.utils.thought_filtering import filter_redundant_thoughts
from src.utils.tools.tool_analysis import get_relevant_tools
from src.utils.logging_utils import log_phase, log_tool_failed, log_tool_skipped
from src.utils.tools.tools_general import summarize_to_query, extract_tool_name

class ReActConsultantAgent:
    """
    A class to review sections of an IT consulting report using the ReAct (Reason + Act) framework with OpenAI's ChatCompletion API.

    Process:
    1. Initializes the agent with the section name and text.
    2. Builds a prompt for the ReAct framework.
    3. Tracks the history of thoughts, actions, and observations.

    Attributes:
    section_name (str): The name of the section to review.
    section_text (str): The text of the section to review.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.
    history (list): A list to store the history of thoughts, actions, and observations.

    Methods:
    build_react_prompt():
        Builds a prompt for the ReAct framework based on the section text and history.
    """

    def __init__(self, section_name, section_text, proposal_text=None, model="gpt-3.5-turbo", temperature=0.7, initial_thought=None):
        """
        Initializes the ReActConsultantAgent with the given section name, section text, model, and temperature.

        Parameters:
        section_name (str): The name of the section to review.
        section_text (str): The text of the section to review.
        proposal_text (str): Full proposal text (or relevant excerpt).
        model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
        temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.
        """
        self.section_name = section_name
        self.section_text = section_text
        self.full_proposal_text = proposal_text
        self.model = model
        self.temperature = temperature
        self.initial_thought = initial_thought  # ✅ NEW: Starting thought from ToT
        self.history = []
        self.tool_usage = {}  # {action_name: count}
        self.memory = {
            "section_notes": {},     # {section_name: [insight1, insight2, ...]}
            "cross_section_flags": [],  # [(sectionA, sectionB, observation)]
            "tool_history": []       # [(step_number, action, section)]
        }

    def build_react_prompt(self):
        """
        Builds a prompt for the ReAct framework based on the section text and history.

        Workflow:
        1. Constructs a base prompt with the section name and text.
        2. Iterates through the history of thoughts, actions, and observations, appending them to the base prompt.
        3. Adds a final line asking for the next thought and action.

        Returns:
        list: A list containing a single dictionary with the role 'user' and the constructed prompt as content.
        """
        base_prompt = (
            f"You are an expert IT strategy consultant reviewing a report section titled '{self.section_name}'.\n"
            "You are using ReAct (Reason + Act) to think through the review.\n\n"
            "Format each response like this:\n"
            "Thought: <your reasoning>\n"
            "Action: <one of: ask_question, flag_risk, recommend_fix, summarize>\n\n"
            f"Here is the section content:\n{self.section_text}\n\n"
        )

        # ✅ Seed with ToT-generated initial thought (if provided)
        if self.initial_thought and len(self.history) == 0:
            base_prompt += f"Thought: {self.initial_thought}\n"

        for step in self.history:
            base_prompt += f"Thought: {step['thought']}\n"
            base_prompt += f"Action: {step['action']}\n"
            base_prompt += f"Observation: {step['observation']}\n\n"

        base_prompt += "What is your next Thought and Action?"

        return [{"role": "user", "content": base_prompt}]

    def build_react_prompt_withTools(self):
            """
            Builds a prompt for the ReAct framework based on the section text and history.
            This prompt is for reviewing a IT report.

            Workflow:
            1. Constructs a base prompt with the section name and text.
            2. Iterates through the history of thoughts, actions, and observations, appending them to the base prompt.
            3. Adds a final line asking for the next thought and action.
            For the check_guideline action, the prompt includes a placeholder for the topic.
            LLM infers topic from the section_text

            Returns:
            list: A list containing a single dictionary with the role 'user' and the constructed prompt as content.
            """
            tool_hint_text, tools_to_focus = build_tool_hints(self)

            base_prompt = (
                f"You are an expert IT strategy consultant reviewing a report section titled '{self.section_name}'.\n"
                "You are using ReAct (Reason + Act) to think through the review.\n\n"
                "Format each response like this:\n"
                "Thought: <your reasoning>\n"
                "Action: <choose ONE tool from the prioritized list below, unless you strongly believe another tool is better>\n\n"
                f"Prioritized tools for this section:\n{tool_hint_text}\n\n"
                "Available tools and their descriptions:\n"
            )

            base_prompt += format_tool_catalog_for_prompt(tool_catalog)
            base_prompt += f"Here is the section content:\n{self.section_text}\n\n"
            
            for step in self.history:
                base_prompt += f"Thought: {step['thought']}\n"
                base_prompt += f"Action: {step['action']}\n"
                base_prompt += f"Observation: {step['observation']}\n\n"

            base_prompt += "What is your next Thought and Action?"

            return [{"role": "user", "content": base_prompt}]
    
    
    def build_react_prompt_forRFPeval(self, criterion, section_text, full_proposal_text, thoughts=None, tool_embeddings=None):
        """
        Builds a ReAct-style prompt for evaluating a vendor proposal using a specific RFP criterion.

        Parameters:
            criterion (str): The RFP evaluation criterion (e.g., "Solution Fit").
            proposal_text (str): Full proposal text (or relevant excerpt).
            thoughts (list): Top thoughts generated from Tree of Thought (optional).
            tool_embeddings (dict): Cached embeddings for tool catalog (required).
        """
        self.section_name = criterion
        self.section_text = section_text
        self.full_proposal_text = full_proposal_text

        # Generate embedding-based tool hints
        if tool_embeddings:
            tool_hint_text, tools_to_focus = build_tool_hints_for_rfp_eval_embedding(
                criterion=criterion,
                proposal_text=section_text,
                thoughts=thoughts,
                tool_embeddings=tool_embeddings
            )
        else:
            tool_hint_text = "None. Pick from Available Tools below."

        # Build the base prompt
        thoughts_text = "\n".join(thoughts) if thoughts else "[Start your own reasoning]"
        base_prompt = (
                f"You are a technology advisor evaluating a vendor proposal against the following RFP criterion:\n"
                f"**{criterion}**\n\n"
                f"The client cares about cost-effectiveness, performance, security, trust, and ease of implementation.\n\n"
                f"Based on the proposal content below, begin your evaluation with a short thought and then choose an action.\n"
                f"Use the tool that best supports your analysis.\n\n"
                f"💡 Thoughts to consider:\n{thoughts_text}\n\n"
                f"🛠️ Format your response like this:\n"
                f"Thought: <your thought>\n"
                f"Action: <one of the tools below>\n\n"
                f"⭐ Recommended tools for this task:\n{tool_hint_text}\n\n"
                f"🧰 Available tools (pick one exactly as shown):\n{format_tool_catalog_for_prompt(tool_catalog)}\n\n"
                f"⚠️ Rules:\n"
                f"- DO NOT invent or explain actions.\n"
                f"- ONLY choose one tool from the list above.\n"
                f"- If no tool fits, use: `summarize`, `ask_question`, or `tool_help`.\n"
                f"- DO NOT output anything else.\n\n"
                f"📄 Section relevant to this criterion:\n{self.section_text}\n\n"
                f"📄 Full Proposal Text:\n{self.full_proposal_text}\n\n"
            )

        base_prompt += "Previous Thoughts, Actions & Observations:\n"
        for step in self.history:
            base_prompt += f"Thought: {step['thought']}\n"
            base_prompt += f"Action: {step['action']}\n"
            base_prompt += f"Observation: {step['observation']}\n\n"

        base_prompt += "What is your next Thought and Action?"

        return [{"role": "user", "content": base_prompt}]




def run_react_loop_check_withTool(agent, max_steps=5, report_sections=None, executed_tools_global=None):
    """
    Runs the ReAct (Reason + Act) loop for a specified number of steps.

    Purpose:
    This function iterates through a reasoning and action loop using the ReAct framework to review a section of an IT consulting report. It generates thoughts, actions, and observations at each step, and stores the history of these steps.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, initialized with the section name and text.
    max_steps (int): The maximum number of steps to run the loop. Default is 5.

    Workflow:
    1. Iterates through the loop for a maximum of `max_steps` times.
    2. In each iteration:
       - Calls `agent.build_react_prompt()` to construct the prompt for the ReAct framework.
       - Calls `call_openai_with_tracking()` to get the response from the OpenAI API.
       - Parses the response to extract the thought and action.
       - Generates an observation based on the action.
       - Stores the thought, action, and observation in the agent's history.
       - Prints the result of the current step.
       - Breaks the loop if the action is "summarize".
    3. Returns the full reasoning history.

    Returns:
    list: A list of dictionaries, where each dictionary contains the thought, action, and observation for each step.
    """
    executed_tools_global = executed_tools_global or set()

    for step_num in range(max_steps):
        messages = agent.build_react_prompt_withTools()
        response = call_openai_with_tracking(messages, model=agent.model, temperature=agent.temperature)

        # Parse response
        try:
            lines = response.strip().split("\n")
            thought = next(line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("thought"))
            action = next(line.split(":", 1)[1].strip() for line in lines if line.lower().startswith("action"))
            # Log tool usage
            if hasattr(agent, "tool_usage"):
                agent.tool_usage[action] = agent.tool_usage.get(action, 0) + 1
        except:
            log_phase("⚠️ Failed to parse model response.")
            break

        # Generate observation based on action
        observation = dispatch_tool_action(
            agent, 
            action, 
            report_sections=report_sections,
            executed_tools_global=executed_tools_global)

        # Track tool history
        agent.memory["tool_history"].append((step_num, action, agent.section_name))

        # Special case for section comparisons
        if action.startswith("compare_with_other_section"):
            match = re.match(r'compare_with_other_section\["(.+?)",\s*"(.+?)"\]', action)
            if match:
                sectionA, sectionB = match.groups()
                agent.memory["cross_section_flags"].append((sectionA, sectionB, observation))

        # Store step
        agent.history.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })
        
        # Print result of this step
        log_phase(f"\n🔁 Step {step_num + 1}")
        log_phase(f"🧠 Thought: {thought}")
        log_phase(f"⚙️ Action: {action}")
        log_phase(f"👀 Observation: {observation}")

        if action == "summarize":
            break
    
    # Summarize and store section notes, scores, fixes, confidence level, raw ouputs
    summarize_and_score_section(agent, report_sections)

    # Return full reasoning history
    return agent.history


def run_single_react_step(agent, thought, action, step_num=0):
    """
    Simulates a single ReAct step using a given thought and action.
    Delegates action execution to dispatch_tool_action().

    Returns:
    - observation: result of executing the tool
    """
    # Log tool usage
    if hasattr(agent, "tool_usage"):
        agent.tool_usage[action] = agent.tool_usage.get(action, 0) + 1

    # Execute the action using shared dispatch function
    observation = dispatch_tool_action(agent, action)

    # Store step in history
    agent.history.append({
        "thought": thought,
        "action": action,
        "observation": observation
    })

    # Track tool usage in memory
    agent.memory["tool_history"].append((step_num, action, agent.section_name))

    return observation


def dispatch_tool_action(
        agent, 
        action, 
        report_sections=None, 
        tool_map=None, 
        raise_errors=False,
        executed_tools_global=None):
    """
    Dispatches and executes the appropriate tool function based on the action string.

    Parameters:
        agent (ReActConsultantAgent): The reasoning agent with context.
        action (str): Action string (e.g., tool_name["some input"]).
        report_sections (dict): Optional full report for context.
        tool_map (dict): Optional override of registered tool functions.
        raise_errors (bool): If True, re-raises exceptions (for debugging).

    Returns:
        str: Result from the tool or error message.
    """
    log_phase(f"🛠️ Tool action: {action}")
    tool_map = tool_map or TOOL_FUNCTION_MAP
    executed_tools_global = executed_tools_global or set()

    try:
        # Parse action string like tool_name["input string"]
        match = re.match(r'^([a-zA-Z0-9_]+)(\["(.*)"\])?$', action)
        if not match:
            log_tool_failed("unknown_tool", f"Could not parse tool action: {action}")
            return f"⚠️ Could not parse tool action: {action}"

        tool_name = match.group(1)
        input_arg = match.group(3) if match.group(2) else None

        if tool_name in executed_tools_global:
            log_tool_skipped(tool_name, f"⚠️ Tool '{tool_name}' already executed for this proposal. Skipping duplicate call.")
            return f"⚠️ Tool '{tool_name}' already executed for this proposal. Skipping duplicate call."

        if tool_name not in tool_map:
            log_tool_failed(tool_name, f"Tool '{tool_name}' not recognized.")
            return f"⚠️ Tool '{tool_name}' not recognized in TOOL_FUNCTION_MAP."

        tool_entry = tool_map[tool_name]
        tool_fn = tool_entry["fn"]
        arg_spec = tool_entry.get("args", [])
 
        # Log argument types
        log_tool_used(tool_name)
        log_phase(f"🔍 Dispatching {tool_name} with args: {arg_spec}")
        log_tool_execution(tool_name, tool_fn, input_arg, agent)
        

        # Call variants
        if arg_spec == ["agent"]:
            result = tool_fn(agent)
        elif arg_spec == ["input_arg"]:
            result = tool_fn(input_arg)
        elif arg_spec == ["agent", "input_arg"]:
            result = tool_fn(agent, input_arg)
        else:
            raise ValueError(f"Unsupported arg spec for tool '{tool_name}': {arg_spec}")

        executed_tools_global.add(tool_name)  # ✅ Mark as executed
        return result
    except Exception as e:
        log_tool_failed(tool_name, f"{tool_name} dispatch failed: {e}")
        if raise_errors:
            raise
        return f"⚠️ Tool execution error: {e}"


def select_best_tool_with_llm(agent, criterion, top_thoughts, model="gpt-3.5-turbo"):
    messages = build_tool_selection_prompt_rfpeval(agent, criterion, top_thoughts)
    response = call_openai_with_tracking(messages, model=model, temperature=0)

    # Clean and return tool action string
    return response.strip().splitlines()[0]  # Example: check_guideline["cloud"]


def run_react_loop_for_rfp_eval(
        agent, 
        criterion, 
        section_text, 
        full_proposal_text, 
        thoughts=None, 
        tool_embeddings=None, 
        report_sections=None, 
        max_steps=4,
        seen_thoughts=None,
        seen_embeddings=None,
        executed_tools_global=None):
    """
    Runs a ReAct loop for RFP evaluation using the new embedding-based prompt builder.

    Parameters:
        agent (ReActConsultantAgent): The agent initialized with section_name and section_text.
        criterion (str): The evaluation criterion (e.g., "Solution Fit").
        proposal_text (str): Full text of the vendor proposal.
        thoughts (list): Tree of Thought-generated reasoning paths (optional).
        tool_embeddings (dict): Cached tool embeddings.
        max_steps (int): Number of ReAct iterations to run.

    Returns:
        list of step dictionaries with thought, action, observation.
    """
    seen_thoughts = seen_thoughts or []
    seen_embeddings = seen_embeddings or []
    executed_tools_global = executed_tools_global or set()

    for step_num in range(max_steps):
        log_phase(f"\n🔁 React Step {step_num + 1} of {max_steps}")
        messages = agent.build_react_prompt_forRFPeval(
            criterion=criterion,
            section_text=section_text,
            full_proposal_text=full_proposal_text,
            thoughts=thoughts,
            tool_embeddings=tool_embeddings
        )
        log_phase(f"Prompt for LLM: {messages}")

        # Run LLM
        if agent.section_text is None: raise ValueError("Section text is None.")
        response = call_openai_with_tracking(messages, model=agent.model, temperature=agent.temperature)

        log_phase(f"LLM response: {response}")

        # Parse response
        try:
            thought, action = parse_thought_action(response)
            log_phase(f"Action: {action}")
            log_phase(f"\n🔁 Step {step_num + 1}")
            log_phase(f"🧠 Thought: {thought}")
            log_phase(f"⚙️ Action: {action}")
        except Exception as e:
            log_phase(f"⚠️ Failed to parse step {step_num + 1}: {str(e)}")
            break
        
        # Check if action is not redundant to previous thoughts
        novel_thoughts, novel_embs = filter_redundant_thoughts([thought], seen_thoughts, seen_embeddings)
        log_deduplication([thought], novel_thoughts)
        if not novel_thoughts:
            log_phase(f"⚠️ Skipping redundant thought: {thought}")
            continue

        seen_thoughts.extend(novel_thoughts) # Store non-redundant thoughts (for future new thought checks)
        seen_embeddings.extend(novel_embs) # Store non-redundant embeddings (for future new thought checks)
        thought = novel_thoughts[0]  # Use cleaned one

        # Run tool
        try:
            observation = dispatch_tool_action(
                agent, 
                action, 
                report_sections=report_sections, 
                executed_tools_global=executed_tools_global,
                raise_errors=True)
            log_phase(f"👀 Observation: {observation}")
            if observation is None:
                observation = "⚠️ Tool returned no result."
        except Exception as e:
            observation = f"⚠️ Tool execution error: {e}"
        log_phase(f"👀 Observation: {observation}")

        # Store in agent history
        agent.history.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })

        if action == "summarize":
            break

    return agent.history

def parse_thought_action(response: str):
    """
    Parses an LLM response into a (thought, action) tuple.

    Parameters:
        response (str): Multiline LLM response with Thought and Action.

    Returns:
        (thought: str, action: str)

    Raises:
        ValueError if parsing fails.
    """
    lines = response.strip().split("\n")
    thought = None
    action = None

    for line in lines:
        line = line.strip()
        if line.lower().startswith("thought:"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                thought = parts[1].strip()
        elif line.lower().startswith("action:"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                action = parts[1].strip()

    if not thought or not action:
        raise ValueError(f"Could not parse Thought or Action from response:\n{response}")

    return thought, action


def run_missing_relevant_tools(
    agent,
    criterion,
    section_text,
    relevant_tools,
    tool_embeddings,
    triggered_tools,
    tool_function_map,
    executed_tools_global=None,
    similarity_threshold=0.75,
    run_score_threshold=0.75,
    verbose=False
):
    """
    Identifies and runs relevant tools based on embedding similarity that were not already triggered.

    Parameters:
        agent: ReActConsultantAgent (provides section context)
        criterion: str
        section_text: str
        tool_embeddings: Dict[str, List[float]]
        triggered_tools: list of already used tools [{tool, result, thought}]
        tool_function_map: dict of {tool_name: function}
        similarity_threshold: float (default 0.75)

    Returns:
        - auto_triggered: list of dicts with tool execution results
        - missing_tools: list of (tool_name, score) pairs
    """
    if executed_tools_global is None:
        executed_tools_global = set()

    tools_used = [extract_tool_name(t["tool"]) for t in triggered_tools]

    auto_triggered = []
    auto_triggered_meta = []

    log_phase("In run_missing_relevant_tools()")
    log_phase(f"tools_used: {tools_used}")
    log_phase(f"relevant_tools: {relevant_tools}")
    for tool_name, score in relevant_tools:
        log_phase(f"Tool: {tool_name}, Score: {score:.3f}")
        log_phase(f"run_score_threshold: {run_score_threshold:.3f}, ")
        if score < run_score_threshold:
            continue
        if tool_name in tools_used:
            continue
        if tool_name in executed_tools_global:
            continue
        if tool_name not in tool_function_map:
            continue

        try:
            tool_fn = tool_function_map[tool_name] # resolve function name in tool_function_map

            log_phase(f"⚙️ Auto-running missing relevant tool: {tool_name} (score: {score})")
            query = "evaluate based on section context"
            action_str = f'{tool_name}["{query}"]'
            log_phase(f"Calling {tool_name} with query: {query}")
            result = dispatch_tool_action(
                agent=agent,
                action=action_str,
                report_sections=None,
                tool_map=tool_function_map,
                raise_errors=False,
                executed_tools_global=executed_tools_global
            )

            auto_triggered.append({  # store meta data
                "tool": tool_name,
                "result": result,
                "thought": f"Auto-invoked based on similarity score {score:.3f}"
            })

            auto_triggered_meta.append({  # store meta data
                "tool": tool_name,
                "criterion": criterion,
                "similarity_score": score,
                "result": result
            })

            executed_tools_global.add(tool_name) # add tool to global executed tools
            log_phase(f"Tool {tool_name} executed successfully.")
        except Exception as e:
            log_tool_failed(tool_name, f"Auto tool call failed: {e}")
            continue

    return auto_triggered, auto_triggered_meta

