# react_agent.py - Core class + reasoning loops

import re
from src.models.openai_interface import call_openai_with_tracking
from src.models.section_tools_llm import auto_fill_gaps_with_research, check_recommendation_alignment, check_summary_support, evaluate_smart_goals, generate_final_summary, should_cite, upgrade_section_with_research
from src.server.prompt_builders import build_tool_hints, format_tool_catalog_for_prompt
from src.models.scoring import summarize_and_score_section
from src.utils.tools.tool_catalog import tool_catalog
from src.utils.tools.tools_basic import check_alignment_with_goals, check_guideline, check_timeline_feasibility, compare_with_other_section, generate_client_questions, highlight_missing_sections, keyword_match_in_section, search_report
from src.utils.tools.tools_nlp import analyze_tone_textblob, check_for_jargon, check_readability, extract_named_entities
from src.utils.tools.tools_reasoning import analyze_math_question, pick_tool_by_intent_fuzzy
from src.utils.tools.tools_web import search_arxiv, search_serpapi, search_web, search_wikipedia, should_search_arxiv


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

    def __init__(self, section_name, section_text, model="gpt-3.5-turbo", temperature=0.7):
        """
        Initializes the ReActConsultantAgent with the given section name, section text, model, and temperature.

        Parameters:
        section_name (str): The name of the section to review.
        section_text (str): The text of the section to review.
        model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
        temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.
        """
        self.section_name = section_name
        self.section_text = section_text
        self.model = model
        self.temperature = temperature
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

        for step in self.history:
            base_prompt += f"Thought: {step['thought']}\n"
            base_prompt += f"Action: {step['action']}\n"
            base_prompt += f"Observation: {step['observation']}\n\n"

        base_prompt += "What is your next Thought and Action?"

        return [{"role": "user", "content": base_prompt}]

    def build_react_prompt_withTools(self):
            """
            Builds a prompt for the ReAct framework based on the section text and history.

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


def run_react_loop_check_withTool(agent, max_steps=5, report_sections=None):
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
            print("⚠️ Failed to parse model response.")
            break

        # Generate observation based on action
        observation = dispatch_tool_action(agent, action, report_sections=report_sections)

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
        print(f"\n🔁 Step {step_num + 1}")
        print(f"🧠 Thought: {thought}")
        print(f"⚙️ Action: {action}")
        print(f"👀 Observation: {observation}")

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


def dispatch_tool_action(agent, action, report_sections=None):
    """
    Purpose:
        Dispatches a tool action based on the provided action string and executes the corresponding function.

    Parameters:
        agent (object): The agent object containing context such as section text, section name, and memory.
        action (str): The action string specifying the tool action to be executed.

    Workflow:
        1. Logs the tool action being executed.
        2. Matches the action string against predefined patterns using regular expressions.
        3. Executes the corresponding function based on the matched action.
        4. Handles specific cases such as academic support, citation checks, and section upgrades.
        5. Returns the result of the executed function or an appropriate message if the action is unrecognized.

    Returns:
        str: The result of the executed tool action or an error message if an exception occurs.
    """
    print(f"🛠️ Tool action: {action}")
    try:
        if action.startswith("check_guideline"):
            match = re.match(r'check_guideline\["(.+?)"\]', action)
            if match:
                return check_guideline(match.group(1))
        elif action.startswith("keyword_match_in_section"):
            match = re.match(r'keyword_match_in_section\["(.+?)"\]', action)
            if match:
                return keyword_match_in_section(match.group(1), agent.section_text)
        elif action.startswith("check_timeline_feasibility"):
            match = re.match(r'check_timeline_feasibility\["(.+?)"\]', action)
            if match:
                return check_timeline_feasibility(match.group(1))
        elif action.startswith("search_report"):
            match = re.match(r'search_report\["(.+?)"\]', action)
            if match:
                return search_report(match.group(1), report_sections)
        elif action.startswith("search_web"):
            match = re.match(r'search_web\["(.+?)"\]', action)
            if match:
                return search_web(match.group(1))
        elif action == "check_for_jargon":
            return check_for_jargon(agent.section_text)
        elif action == "generate_client_questions":
            return generate_client_questions(agent.section_text)
        elif action == "highlight_missing_sections":
            return highlight_missing_sections(report_sections)
        elif action.startswith("check_alignment_with_goals"):
            match = re.match(r'check_alignment_with_goals\["(.+?)"\]', action)
            if match:
                return check_alignment_with_goals(match.group(1), report_sections)
        elif action.startswith("compare_with_other_section"):
            match = re.match(r'compare_with_other_section\["(.+?)",\s*"(.+?)"\]', action)
            if match:
                return compare_with_other_section(match.group(1), match.group(2), report_sections)
        elif action.startswith("check_summary_support"):
            match = re.match(r'check_summary_support\["(.+?)"\]', action)
            if match:
                return check_summary_support(match.group(1), report_sections)
        elif action == "evaluate_smart_goals":
            return evaluate_smart_goals(agent.section_text)
        elif action.startswith("check_recommendation_alignment"):
            match = re.match(r'check_recommendation_alignment\["(.+?)"\]', action)
            if match:
                goals = report_sections.get("Goals & Objectives", "")
                return check_recommendation_alignment(match.group(1), goals)
        elif action == "ask_question":
            return "Good question to ask the client for clarification."
        elif action == "flag_risk":
            return "This is a legitimate risk that should be addressed."
        elif action == "recommend_fix":
            return "The recommendation improves the section's clarity and compliance."
        elif action == "summarize":
            return "Review complete."
        elif action == "tool_help":
            return format_tool_catalog_for_prompt(tool_catalog)
        elif action.startswith("suggest_tool_for"):
            match = re.match(r'suggest_tool_for\["(.+?)"\]', action)
            if match:
                matches = pick_tool_by_intent_fuzzy(match.group(1), tool_catalog)
                if matches:
                    return "Best match based on your goal:\n" + "\n".join([f"{tool} (match: {score})" for tool, score in matches])
                else:
                    return "⚠️ No matching tool found. Showing available tools:\n" + format_tool_catalog_for_prompt(tool_catalog)
        elif action == "final_summary":
            return generate_final_summary(agent)
        elif action == "check_readability": 
            return check_readability(agent.section_text)
        elif action.startswith("search_wikipedia"):
            match = re.match(r'search_wikipedia\["(.+?)"\]', action)
            if match:
                query = match.group(1)
                return search_wikipedia(query)
            else:
                return "⚠️ Could not parse search_wikipedia action."
        elif action == "analyze_tone_textblob":
            return analyze_tone_textblob(agent.section_text)
        elif action.startswith("search_serpapi"):
            match = re.match(r'search_serpapi\["(.+?)"\]', action)
            if match:
                query = match.group(1)
                return search_serpapi(query, agent)
            else:
                return "⚠️ Could not parse search_serpapi action."
        elif action == "extract_named_entities":
            return extract_named_entities(agent.section_text)
        elif action.startswith("analyze_math_question"):
            match = re.match(r'analyze_math_question\["(.+?)"\]', action)
            if match:
                expr = match.group(1)
                return analyze_math_question(expr)
            else:
                return "⚠️ Could not parse analyze_math_question action."
        elif action.startswith("search_arxiv"):
            match = re.match(r'search_arxiv\["(.+?)"\]', action)
            if match:
                query = match.group(1)
                return search_arxiv(query, agent)
            else:
                return "⚠️ Could not parse search_arxiv action."
        elif action == "auto_check_for_academic_support":
            needs_citation, reason = should_search_arxiv(agent.section_text)
            if needs_citation:
                # Automatically create and run an arxiv search
                followup_action = f'search_arxiv["{agent.section_name}"]'
                followup_obs = dispatch_tool_action(agent, followup_action, report_sections)
                # Log follow-up to memory
                agent.memory.setdefault("academic_support", {})[agent.section_name] = {
                    "reason": reason,
                    "action": followup_action,
                    "observation": followup_obs
                }
                return f"✅ Academic support was added.\nReason: {reason}\n\n{followup_obs}"
            else:
                return f"🟢 No academic support needed.\nReason: {reason}"
        elif action.startswith("should_cite"):
            match = re.match(r'should_cite\["(.+?)"\]', action)
            if match:
                statement = match.group(1)
                needs, reason = should_cite(statement)
                if needs:
                    # Run research-based rewrite
                    improved = auto_fill_gaps_with_research(statement)
                    observation = (
                        f"✅ Citation recommended. Reason: {reason}\n\n"
                        f"📚 Improved statement with research:\n{improved}"
                    )
                    agent.memory.setdefault("enhanced_statements", {})[statement] = improved
                    return observation
                else:
                    observation = f"🟢 No citation needed. Reason: {reason}"
                    return observation
            else:
                return "⚠️ Could not parse should_cite action."
        elif action == "auto_fill_gaps_with_research":
            return auto_fill_gaps_with_research(agent.section_text)
        elif action == "upgrade_section_with_research":
            improved, log, footnotes = upgrade_section_with_research(agent.section_text)
            observation = "🧠 Section upgraded with research. Rewrites:\n"
            for change in log:
                observation += f"- 🔹 '{change['original']}'\n  🧠 → {change['improved']}\n  📚 Reason: {change['reason']}\n\n"

            # Store in memory for final report
            agent.memory.setdefault("section_upgrades", {})[agent.section_name] = {
                "original": agent.section_text,
                "improved": improved,
                "log": log,
                "footnotes": footnotes
            }

            return observation
        else:
            return "Unrecognized action."
    except Exception as e:
        return f"⚠️ Tool execution error: {str(e)}"
        
