# scoring.py – Scoring, confidence, fix suggestions

from src.models.openai_interface import call_openai_with_tracking
import re

def score_section(section_name, section_text, goals_text=None, model="gpt-3.5-turbo", temperature=0.6):
    """
    Scores a section of a consulting report based on clarity, alignment, and completeness.

    Purpose:
    This function evaluates a specified section of a consulting report using three criteria: clarity, alignment with goals, and completeness. It generates a score out of 10 for each criterion along with a one-line explanation for each score.

    Parameters:
    section_name (str): The name of the section to evaluate.
    section_text (str): The text of the section to evaluate.
    goals_text (str, optional): The text of the report's goals to evaluate alignment. Default is None.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.6.

    Workflow:
    1. Constructs a prompt that instructs the model to evaluate the section based on clarity, alignment, and completeness.
    2. If goals_text is provided, includes it in the prompt for evaluating alignment.
    3. Creates a list of messages with the constructed prompt.
    4. Calls the OpenAI API with tracking using the call_openai_with_tracking function.
    5. If the API call is successful, returns the generated scores and explanations.
    6. If an exception occurs, returns a failure message with the exception details.

    Returns:
    str: The generated scores and explanations for clarity, alignment, and completeness, or a failure message if the API call fails.
    """
    prompt = (
        f"Evaluate the section '{section_name}' of a consulting report using the following 3 criteria:\n"
        "1. Clarity (Is the writing clear, well-structured, and understandable?)\n"
        "2. Alignment (Does it align with the report’s goals?)\n"
        "3. Completeness (Does it cover the necessary topics?)\n\n"
    )

    if goals_text:
        prompt += f"Report Goals:\n{goals_text}\n\n"

    prompt += f"Section:\n{section_text}\n\n"
    prompt += (
        "Provide a score out of 10 for each criterion with a one-line explanation per score. Format:\n"
        "Clarity: [score]/10 – [reason]\n"
        "Alignment: [score]/10 – [reason]\n"
        "Completeness: [score]/10 – [reason]\n"
    )

    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages, model=model, temperature=temperature)
        return response.strip()
    except Exception as e:
        return f"⚠️ Failed to score section: {str(e)}"


def summarize_section_insights(agent, model="gpt-3.5-turbo", temperature=0.7):
    """
    Summarize key insights from this section's reasoning steps into a short, client-friendly paragraph.
    """
    steps = agent.history[-5:]  # Last 5 steps, or you could use all
    thoughts = "\n".join([f"Thought: {s['thought']}\nAction: {s['action']}\nObservation: {s['observation']}" for s in steps])

    prompt = (
        f"You are summarizing an internal AI review of the consulting report section '{agent.section_name}'.\n"
        "Write a concise, client-facing summary of the most important observations based on the review.\n"
        "Focus on useful insights, potential risks, and gaps. Avoid tool names or internal system messages.\n\n"
        f"Review Log:\n{thoughts}\n\n"
        "Summary:"
    )

    messages = [{"role": "user", "content": prompt}]
    try:
        return call_openai_with_tracking(messages, model=model, temperature=temperature).strip()
    except Exception as e:
        return f"⚠️ Failed to summarize section insights: {str(e)}"


def get_confidence_level(agent, model="gpt-3.5-turbo", temperature=0.6):
    """
    Evaluates the confidence level of the AI consultant's reasoning steps.

    Purpose:
    This function assesses the confidence level of the AI consultant's reasoning steps based on clarity, consistency, and support of the analysis. It uses the OpenAI API to rate the confidence level from 1 to 10.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the reasoning history to be evaluated.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.6.

    Workflow:
    1. Extracts the last 5 reasoning steps from the agent's history.
    2. Constructs a prompt that includes the reasoning steps and asks for a confidence level rating from 1 to 10.
    3. Creates a list of messages with the constructed prompt.
    4. Calls the OpenAI API with tracking using the call_openai_with_tracking function.
    5. If the API call is successful, returns the confidence level rating.
    6. If an exception occurs, returns a warning message.

    Returns:
    str: The confidence level rating from 1 to 10, or a warning message if the API call fails.
    """
    reasoning_log = "\n".join([f"{s['thought']} → {s['action']} → {s['observation']}" for s in agent.history[-5:]])
    prompt = (
        "Given the following reasoning steps from an AI consultant reviewing a report section, rate the confidence "
        "level from 1 to 10 based on how clear, consistent, and well-supported the analysis appears. Just return a number (1–10).\n\n"
        f"{reasoning_log}\n\nConfidence Level:"
    )
    messages = [{"role": "user", "content": prompt}]
    try:
        return call_openai_with_tracking(messages, model=model, temperature=temperature).strip()
    except Exception as e:
        return "⚠️"


def recommend_fixes(agent, model="gpt-3.5-turbo", temperature=0.7):
    """
    Generates specific fixes or improvements for a consulting report section.

    Purpose:
    This function reviews the notes for a specific section of a consulting report and generates 2-3 specific fixes or improvements to make the section stronger.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data to be reviewed.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.

    Workflow:
    1. Retrieves the notes for the current section from the agent's memory.
    2. Constructs a prompt that includes the section notes and asks for 2-3 specific fixes or improvements.
    3. Creates a list of messages with the constructed prompt.
    4. Calls the OpenAI API with tracking using the call_openai_with_tracking function.
    5. If the API call is successful, returns the generated fixes or improvements.
    6. If an exception occurs, returns a failure message with the exception details.

    Returns:
    str: The generated fixes or improvements, or a failure message if the API call fails.
    """
    notes = agent.memory["section_notes"].get(agent.section_name, [""])[0]

    prompt = (
        f"You are reviewing this consulting section:\n\n{notes}\n\n"
        "List 2–3 specific fixes or improvements to make this section stronger."
    )

    messages = [{"role": "user", "content": prompt}]
    try:
        return call_openai_with_tracking(messages, model=model, temperature=temperature).strip()
    except Exception as e:
        return f"⚠️ Failed to generate fixes: {str(e)}"


def extract_top_issues(agent, model="gpt-3.5-turbo", temperature=0.7):
    """
    Extracts the top 3 most important issues or gaps from the section summaries in the agent's memory.

    Purpose:
    This function reviews feedback across multiple sections of a report and identifies the top 3 most important issues or gaps that should be addressed. It prioritizes issues that impact clarity, alignment, or completeness across the report.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data to be reviewed.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.

    Workflow:
    1. Retrieves the section summaries from the agent's memory.
    2. Concatenates the section summaries into a single string.
    3. Constructs a prompt instructing the model to identify the top 3 most important issues or gaps based on the section summaries.
    4. Creates a list of messages with the constructed prompt.
    5. Calls the OpenAI API with tracking using the call_openai_with_tracking function.
    6. If the API call is successful, returns the extracted top issues.
    7. If an exception occurs, returns a failure message with the exception details.

    Returns:
    str: The extracted top 3 issues or gaps, or a failure message if the API call fails.
    """
    summaries = agent.memory.get("section_notes", {})
    all_text = "\n".join([f"{sec}: {obs[0]}" for sec, obs in summaries.items()])

    prompt = (
        "You are an AI consultant reviewing feedback across multiple sections of a report.\n"
        "Based on the following section summaries, identify the top 3 most important issues or gaps that should be addressed.\n"
        "Be concise, specific, and prioritize issues that impact clarity, alignment, or completeness across the report.\n\n"
        f"Section Summaries:\n{all_text}\n\n"
        "Top 3 Issues:"
    )

    messages = [{"role": "user", "content": prompt}]
    try:
        return call_openai_with_tracking(messages, model=model, temperature=temperature).strip()
    except Exception as e:
        return f"⚠️ Failed to extract top issues: {str(e)}"


def format_score_block(score_text):
    """
    Formats a block of score text by adding icons based on the score.

    Purpose:
    This function processes a block of text containing scores out of 10 and adds icons to each line based on the score. The icons indicate the quality of the score: green for high scores, yellow for medium scores, and red for low scores.

    Parameters:
    score_text (str): A block of text containing scores out of 10.

    Workflow:
    1. Splits the input score_text into individual lines.
    2. For each line, searches for a score in the format "X/10".
    3. If a score is found:
       - Adds a green icon (🟢) for scores 8 and above.
       - Adds a yellow icon (🟡) for scores between 6 and 7.
       - Adds a red icon (🔴) for scores below 6.
    4. If no score is found, the line remains unchanged.
    5. Joins the processed lines back into a single block of text.

    Returns:
    str: The formatted block of text with icons added based on the scores.
    """
    def add_icons(line):
        match = re.search(r"(\d+)/10", line)
        if not match:
            return line
        score = int(match.group(1))
        if score >= 8:
            icon = "🟢"
        elif score >= 6:
            icon = "🟡"
        else:
            icon = "🔴"
        return f"{icon} {line}"
    
    return "".join([add_icons(line) + "  \n" for line in score_text.splitlines()])


def summarize_and_score_section(agent, report_sections):
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
