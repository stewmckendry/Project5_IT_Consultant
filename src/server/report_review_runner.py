# report_review_runner.py – Full report orchestration

from models.openai_interface import call_openai_with_tracking
from models.scoring import extract_top_issues, get_confidence_level, recommend_fixes, score_section, summarize_section_insights
from models.section_tools_llm import analyze_missing_sections, generate_final_summary
from src.server.react_agent import ReActConsultantAgent, run_react_loop_check_withTool
from utils.tools.tools_basic import highlight_missing_sections  # Ensure this module exists and is correctly implemented

def run_full_report_review(agent, report_sections, max_steps=5):
    """
    Conducts a full review of an IT consulting report using the ReAct framework.

    Purpose:
    This function iterates through all sections of an IT consulting report, performing a reasoning and action loop for each section using the ReAct framework. It then performs post-processing steps to highlight missing sections, generate a final summary, and extract the top issues.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, initialized with the section name and text.
    report_sections (dict): A dictionary where keys are section headers and values are the corresponding section contents.
    max_steps (int): The maximum number of steps to run the loop for each section. Default is 5.

    Workflow:
    1. Iterates through each section in the report_sections dictionary.
    2. For each section:
       - Sets the agent's section_name and section_text attributes.
       - Calls the run_react_loop_check_withTool function to perform the reasoning and action loop.
    3. After processing all sections, performs post-processing steps:
       - Calls highlight_missing_sections to identify any missing sections in the report.
       - Calls generate_final_summary to generate a final summary of the report.
       - Calls extract_top_issues to identify the top issues or gaps in the report.
    4. Stores the results of the post-processing steps in the agent's memory.

    Returns:
    ReActConsultantAgent: The agent instance with updated memory containing the results of the full report review.
    """
    # Create a single agent to hold memory across sections
    agent = ReActConsultantAgent(section_name="Full Report", section_text="")

    # Loop through all sections
    for section_name, section_text in report_sections.items():
        agent.section_name = section_name
        agent.section_text = section_text
        run_react_loop_check_withTool(agent, max_steps=max_steps)

    # Post-processing steps
    agent.memory["highlight_missing"] = highlight_missing_sections(report_sections)
    agent.memory["missing_analysis"] = analyze_missing_sections(report_sections)
    agent.memory["final_summary"] = generate_final_summary(agent)
    agent.memory["top_issues"] = extract_top_issues(agent)

    return agent


def summarize_full_review(agent):
    """
    Summarizes the full review of an IT consulting report.

    Purpose:
    This function consolidates the feedback from all reviewed sections of an IT consulting report and generates a final summary. The summary highlights the overall quality of the report, identifies gaps, strengths, and suggests next steps for improvement.

    Parameters:
    agent (ITReportReviewer): An instance of the ITReportReviewer class, which contains the review history for each section.

    Workflow:
    1. Initializes an empty string `combined_review_text` to store the consolidated feedback.
    2. Iterates through the `review_history` attribute of the `agent` object.
       - For each review, appends the section name and feedback to `combined_review_text`.
    3. Constructs a prompt for the OpenAI API to summarize the overall quality of the report.
       - The prompt includes the consolidated feedback and instructions to highlight gaps, strengths, and next steps.
    4. Calls the OpenAI API using the `call_openai_with_tracking` function to generate the summary.
    5. Returns the generated summary.

    Returns:
    str: A summary of the overall quality of the report, including gaps, strengths, and suggested next steps.
    """
    # Combine all reviews into a single prompt
    combined_review_text = ""
    for step in agent.review_history:
        combined_review_text += f"Section: {step['section']}\nFeedback: {step['review']}\n\n"

    # Build new prompt asking for a final report assessment
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert IT strategy consultant reviewing an internal report assessment. "
                "Summarize the overall quality of the report based on the following section reviews. "
                "Highlight gaps, strengths, and suggest next steps to improve the report."
            )
        },
        {
            "role": "user",
            "content": combined_review_text
        }
    ]

    summary = call_openai_with_tracking(messages)
    return summary


def summarize_and_score_section(agent):
    section_name = agent.section_name
    section_text = agent.section_text
    goals_text = report_sections.get("Goals & Objectives", None)

    # Summarize
    agent.memory["section_notes"][section_name] = [summarize_section_insights(agent)]

    # Score
    agent.memory.setdefault("section_scores", {})[section_name] = score_section(section_name, section_text, goals_text)

    # Confidence
    agent.memory.setdefault("confidence_levels", {})[section_name] = get_confidence_level(agent)

    # Fix suggestions
    agent.memory.setdefault("section_fixes", {})[section_name] = recommend_fixes(agent)

    # Debug notes
    agent.memory.setdefault("debug_notes", {})[section_name] = agent.history
