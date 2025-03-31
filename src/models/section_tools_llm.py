# section_tools_llm.py – Advanced LLM-based section tools

import re
from src.models.openai_interface import call_openai_with_tracking
from nltk.tokenize import sent_tokenize
from src.utils.tools.tools_web import search_arxiv
from src.utils.section_map import canonical_section_map


def check_summary_support(summary_text, other_sections):
    """
    Check if the summary reflects content from the rest of the report.
    """
    combined = "\n".join(other_sections.values())
    prompt = (
        "Does the following summary accurately reflect the details and points made in the full report?\n\n"
        f"Summary:\n{summary_text}\n\n"
        f"Report Body:\n{combined}\n\n"
        "Answer in 3–5 sentences highlighting any gaps, overstatements, or missing support."
    )
    messages = [{"role": "user", "content": prompt}]
    return call_openai_with_tracking(messages)


def evaluate_smart_goals(agent):
    """
    Evaluate whether the section's goals follow the SMART criteria.
    """
    section_text = agent.section_text
    prompt = (
        "Evaluate the following goals using the SMART criteria:\n"
        "Specific, Measurable, Achievable, Relevant, Time-bound.\n\n"
        f"Goals:\n{section_text}\n\n"
        "Rate each of the SMART attributes and explain briefly."
    )
    messages = [{"role": "user", "content": prompt}]
    return call_openai_with_tracking(messages)


def check_recommendation_alignment(recommendation_text, goals_text):
    """
    Check if recommendations align with the stated goals.
    """
    prompt = (
        f"Here are the goals of the report:\n{goals_text}\n\n"
        f"And here are the key recommendations:\n{recommendation_text}\n\n"
        "Do the recommendations clearly align with the goals? Identify any mismatches or missing connections."
    )
    messages = [{"role": "user", "content": prompt}]
    return call_openai_with_tracking(messages)


def analyze_missing_sections(report_sections):
    """
    Analyzes missing sections in an IT consulting report and evaluates their impact.

    Purpose:
    This function identifies any missing sections in an IT consulting report based on a predefined set of expected sections. It then evaluates how the absence of these sections might affect the report's effectiveness, highlighting any critical omissions.

    Parameters:
    report_sections (dict): A dictionary where keys are section headers and values are the corresponding section contents.

    Workflow:
    1. Identifies the missing sections by comparing the keys in `report_sections` with the expected sections in `canonical_section_map`.
    2. If no sections are missing, returns a message indicating that no critical sections are missing.
    3. If there are missing sections, constructs a prompt listing the missing sections and asking how their absence might affect the report's effectiveness.
    4. Calls the OpenAI API with tracking using the `call_openai_with_tracking` function to get the evaluation.
    5. Returns the evaluation from the OpenAI API.

    Returns:
    str: The evaluation of the impact of the missing sections on the report's effectiveness, or a message indicating that no critical sections are missing.
    """
    missing = list(set(canonical_section_map.keys()) - set(report_sections.keys()))
    if not missing:
        return "✅ No critical sections appear to be missing from the report."

    missing_str = "\n".join(f"- {s}" for s in sorted(missing))

    prompt = (
        "You're reviewing an IT consulting report.\n"
        "The following expected sections are missing:\n"
        f"{missing_str}\n\n"
        "Based on standard consulting practices, how might these missing sections affect the report's effectiveness?\n"
        "Highlight if any of these are critical omissions, and explain why."
    )

    messages = [{"role": "user", "content": prompt}]
    return call_openai_with_tracking(messages)


def should_cite(statement, model="gpt-3.5-turbo", temperature=0.4):
    """
    Uses LLM to evaluate whether a statement or claim would benefit from a citation.

    Returns:
    Tuple: (decision: YES/NO, reason: explanation string)
    """
    prompt = (
        "You're reviewing a statement from an IT strategy report.\n"
        "Should this statement be supported by an external source or citation?\n\n"
        f"Statement:\n\"{statement}\"\n\n"
        "Respond in this format:\n"
        "Decision: YES or NO\n"
        "Reason: [short explanation]"
    )

    messages = [{"role": "user", "content": prompt}]
    response = call_openai_with_tracking(messages, model=model, temperature=temperature)

    decision_match = re.search(r"Decision:\s*(YES|NO)", response, re.IGNORECASE)
    reason_match = re.search(r"Reason:\s*(.+)", response, re.IGNORECASE)

    decision = decision_match.group(1).strip().upper() if decision_match else "NO"
    reason = reason_match.group(1).strip() if reason_match else "No explanation provided."

    return decision == "YES", reason


def auto_fill_gaps_with_research(section_text, model="gpt-3.5-turbo", temperature=0.7):
    """
    Expands vague or underdeveloped parts of the section using reasoning + research context.
    """
    # 1. Ask the LLM what is vague and how to improve it
    guidance_prompt = (
        "You are reviewing a consulting report section that may be vague or incomplete.\n"
        "Suggest what areas could be expanded and what additional research might help.\n\n"
        f"Section:\n{section_text}\n\n"
        "Respond in this format:\n"
        "Gap: [what's missing or vague]\n"
        "Suggested Search Query: [what we could search to improve it]"
    )

    try:
        guidance = call_openai_with_tracking([{"role": "user", "content": guidance_prompt}], model=model, temperature=temperature)

        # 2. Extract suggested search
        match = re.search(r"Suggested Search Query:\s*(.+)", guidance)
        query = match.group(1).strip() if match else "best practices for IT modernization"

        # 3. Run web or arXiv search
        research = search_arxiv(query)

        # 4. Ask the LLM to rewrite the section using research
        improve_prompt = (
            f"Use this research to improve the following section:\n\n"
            f"Section:\n{section_text}\n\n"
            f"Research:\n{research}\n\n"
            "Provide the revised section with clearer, more complete content."
        )

        improved = call_openai_with_tracking([{"role": "user", "content": improve_prompt}], model=model, temperature=temperature)
        return improved.strip()

    except Exception as e:
        return f"⚠️ Tool execution error: {str(e)}"


def upgrade_section_with_research(section_text, model="gpt-3.5-turbo"):
    """
    Enhances a section of text by identifying sentences that require citations and improving them with research.

    Purpose:
    This function processes a given section of text, identifies sentences that would benefit from citations, 
    and enhances them by filling gaps with research. It appends footnotes to the improved sentences and 
    generates a log of changes and footnotes for reference.

    Parameters:
    section_text (str): The text of the section to be enhanced.
    model (str): The name of the AI model to use for evaluating citation needs and generating improvements. 
                 Default is "gpt-3.5-turbo".

    Workflow:
    1. Splits the input text into individual sentences using `sent_tokenize`.
    2. Iterates through each sentence:
       - Calls `should_cite` to determine if the sentence requires a citation.
       - If a citation is needed:
         a. Calls `auto_fill_gaps_with_research` to generate an improved version of the sentence.
         b. Appends the improved sentence with a footnote reference to the enhanced text.
         c. Logs the original sentence, improved sentence, reason for citation, and footnote ID.
       - If no citation is needed, appends the original sentence to the enhanced text.
    3. Combines the enhanced sentences into a single improved text.
    4. Returns the improved text, a log of changes, and a list of footnotes.

    Returns:
    tuple:
        - str: The improved text with enhanced sentences and footnote references.
        - list: A log of changes, where each entry contains:
            - original (str): The original sentence.
            - improved (str): The improved sentence.
            - reason (str): The reason for requiring a citation.
            - footnote (int): The footnote ID.
        - list: A list of footnotes, where each entry contains:
            - footnote_id (int): The ID of the footnote.
            - original (str): The original sentence.
            - improved (str): The improved sentence.
            - reason (str): The reason for requiring a citation.
    """
    sentences = sent_tokenize(section_text)
    enhanced_sentences = []
    log = []
    footnotes = []

    footnote_id = 1

    for sentence in sentences:
        needs_cite, reason = should_cite(sentence, model=model)

        if needs_cite:
            improved = auto_fill_gaps_with_research(sentence)
            tagged = f"{improved.strip()}[^${footnote_id}]"
            enhanced_sentences.append(tagged)
            footnotes.append((footnote_id, sentence, improved.strip(), reason))
            log.append({
                "original": sentence,
                "improved": improved,
                "reason": reason,
                "footnote": footnote_id
            })
            footnote_id += 1
        else:
            enhanced_sentences.append(sentence)

    improved_text = " ".join(enhanced_sentences)
    return improved_text, log, footnotes


def make_text_coherent(enhanced_sentences, model="gpt-3.5-turbo"):
    """
    Improves the coherence and flow of a rewritten section of a report.

    Purpose:
    This function takes a list of enhanced sentences and ensures that the resulting text flows well, 
    removes redundant ideas, and improves transitions between sentences. It uses an AI model to 
    refine the text while preserving all meaningful content.

    Parameters:
    enhanced_sentences (list): A list of sentences that have been enhanced or rewritten.
    model (str): The name of the AI model to use for improving the text. Default is "gpt-3.5-turbo".

    Workflow:
    1. Joins the list of enhanced sentences into a single block of text.
    2. Constructs a prompt instructing the AI model to improve the coherence, remove redundancy, 
       and enhance transitions in the text.
    3. Sends the prompt to the AI model using the `call_openai_with_tracking` function.
    4. Receives the improved version of the text from the AI model.
    5. Returns the improved text as a string.

    Returns:
    str: The improved version of the text with better coherence, transitions, and flow.
    """
    joined = " ".join(enhanced_sentences)
    prompt = (
        "You are a consultant improving a rewritten section of a report. "
        "Ensure the following text flows well, removes redundant ideas, and improves transitions. "
        "Preserve all meaningful content.\n\n"
        f"Text:\n{joined}\n\n"
        "Return the improved version:"
    )
    return call_openai_with_tracking([{"role": "user", "content": prompt}], model=model).strip()


def generate_final_summary(agent, model="gpt-3.5-turbo", temperature=0.7):
    """
    Generates a final summary for the client based on the agent's memory of section insights and cross-section observations.

    Purpose:
    This function constructs a prompt using the agent's memory of section insights and cross-section observations to generate a final summary for the client. It uses the OpenAI API to create a concise summary covering strengths, issues, and overall alignment with goals.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data to be used for generating the summary.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.7.

    Workflow:
    1. Retrieves section notes and cross-section observations from the agent's memory.
    2. Constructs a prompt that includes the section insights and cross-section observations.
    3. Adds instructions to write a short, clear 4-6 sentence final summary covering strengths, issues, and overall alignment with goals.
    4. Creates a list of messages with the constructed prompt.
    5. Calls the OpenAI API with tracking using the call_openai_with_tracking function.
    6. If the API call is successful, returns the generated summary.
    7. If an exception occurs, returns a failure message with the exception details.

    Returns:
    str: The generated final summary or a failure message if the API call fails.
    """
    # Build a summary prompt using memory
    notes_by_section = agent.memory.get("section_notes", {})
    cross_section = agent.memory.get("cross_section_flags", [])

    prompt = "You are a senior consultant wrapping up your review of an IT strategy report.\n"
    prompt += "Use the following section insights and cross-section observations to write a final summary for the client.\n\n"

    for section, notes in notes_by_section.items():
        prompt += f"Section: {section}\n"
        for note in notes:
            prompt += f"- {note}\n"
        prompt += "\n"

    if cross_section:
        prompt += "Cross-Section Findings:\n"
        for a, b, obs in cross_section:
            prompt += f"- {a} vs. {b}: {obs}\n"
        prompt += "\n"

    # Include overall score summary
    if "section_scores" in agent.memory:
        prompt += "\nOverall Ratings:\n"
        for section, score_text in agent.memory["section_scores"].items():
            prompt += f"{section}:\n{score_text}\n\n"
            
    prompt += "Write a short, clear 4-6 sentence final summary covering strengths, issues, and overall alignment with goals."

    messages = [{"role": "user", "content": prompt}]
    
    try:
        return call_openai_with_tracking(messages, model=model, temperature=temperature).strip()
    except Exception as e:
        return f"⚠️ Failed to generate final summary: {str(e)}"


def format_upgraded_sections(agent):
    """
    Formats the upgraded sections of a report with research enhancements into a markdown block.

    Purpose:
    This function retrieves the upgraded sections stored in the agent's memory, formats them into a markdown string, 
    and includes footnotes for any research-based improvements. It provides a clear and structured summary of 
    the enhancements made to each section.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the memory data 
                                  with upgraded sections and their corresponding footnotes.

    Workflow:
    1. Initializes a list with a header for the section improvements.
    2. Retrieves the upgraded sections from the agent's memory under the "section_upgrades" key.
    3. If no upgrades are found, appends a message indicating no upgrades were made and returns the formatted string.
    4. Iterates through each upgraded section:
       - Adds the section name as a subheader.
       - Appends the improved section text with footnotes.
       - If footnotes are available, appends a list of footnotes with the original text, improved text, and reason for the improvement.
    5. Joins the list of lines into a single markdown-formatted string.

    Returns:
    str: A markdown-formatted string containing the upgraded sections with research enhancements and footnotes.
    """
    lines = ["## ✨ Section Improvements with Research\n"]

    upgrades = agent.memory.get("section_upgrades", {})
    if not upgrades:
        lines.append("_No upgrades were made._")
        return "\n".join(lines)

    for section, data in upgrades.items():
        lines.append(f"\n### 🔹 {section}")
        lines.append("**Improved Section (with footnotes):**\n")
        lines.append(data['improved'].strip())

        if "footnotes" in data and data["footnotes"]:
            lines.append("\n**Footnotes:**\n")
            for idx, original, improved, reason in data["footnotes"]:
                lines.append(f"[^{idx}]: Originally: *{original.strip()}*")
                lines.append(f"      → *{improved.strip()}*")
                lines.append(f"      📚 Reason: {reason}\n")

    return "\n".join(lines)
