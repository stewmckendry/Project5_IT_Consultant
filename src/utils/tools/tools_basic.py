# tools_basic.py – Basic report review tools

# Simulated best practices reference data
import re
from src.models.openai_interface import call_openai_with_tracking
from src.utils.section_map import canonical_section_map


best_practices = {
    "cloud security": "Follow NIST Cybersecurity Framework. Include access control, encryption at rest/in-transit, and regular audits.",
    "data governance": "Establish data stewards, quality standards, lifecycle rules, and metadata documentation.",
    "migration": "Use phased migration, sandbox testing, rollback planning, and stakeholder communication."
}

def check_guideline(topic):
    """
    Checks for best practices related to a given topic.

    Purpose:
    This function looks up best practices for a specified topic from a predefined dictionary of best practices.

    Parameters:
    topic (str): The topic for which best practices are to be checked.

    Workflow:
    1. The function converts the topic to lowercase to ensure case-insensitive matching.
    2. It looks up the topic in the `best_practices` dictionary.
    3. If a matching guideline is found, it returns the guideline.
    4. If no matching guideline is found, it returns a message indicating that no matching guideline was found.

    Returns:
    str: The best practice guideline for the specified topic, or a message indicating no matching guideline was found.
    """
    return best_practices.get(topic.lower(), "No matching guideline found.")


def keyword_match_in_section(term, section_text):
    """
    Checks if a keyword or concept is explicitly mentioned in a section of the report.

    Purpose:
    This function helps validate whether the report includes key elements by checking if a specified keyword or concept is mentioned in the section text.

    Parameters:
    term (str): The keyword or concept to search for in the section.
    section_text (str): The text of the section to search within.

    Workflow:
    1. Converts the keyword and section text to lowercase to ensure case-insensitive matching.
    2. Checks if the keyword is present in the section text.
    3. Returns a message indicating whether the keyword was found or not.

    Returns:
    str: A message indicating whether the keyword was found in the section.
    """
    term_lower = term.lower()
    if term_lower in section_text.lower():
        return f"The keyword '{term}' was found in the section."
    else:
        return f"The keyword '{term}' was NOT found in the section."


# Tool #3: Check feasibility of timeline for IT migration
# This tool helps the agent assess the feasibility of a timeline for an IT migration project.
# It checks if the timeline is too short, potentially feasible, or reasonable for a full migration.

def check_timeline_feasibility(duration_str):
    """
    Checks the feasibility of a timeline for an IT migration project.

    Purpose:
    This function helps assess whether a given timeline for an IT migration project is too short, potentially feasible, or reasonable.

    Parameters:
    duration_str (str): The timeline duration as a string (e.g., "6-12 months", "8 to 10 weeks", "a few months").

    Workflow:
    1. Converts the duration string to lowercase and strips any leading/trailing whitespace.
    2. Initializes a dictionary of fuzzy terms (e.g., "a few", "several") with their estimated numeric values.
    3. Checks if the duration string contains any fuzzy terms and estimates the duration in months.
    4. If no fuzzy terms are found, checks for ranges (e.g., "6-12 months") or single values (e.g., "6 months") and calculates the average duration in months.
    5. If the duration cannot be parsed, returns a warning message.
    6. Evaluates the feasibility of the timeline based on the calculated duration in months:
       - If less than 3 months, returns that the timeline is likely too short.
       - If between 3 and 12 months, returns that the timeline is potentially feasible.
       - If more than 12 months, returns that the timeline seems reasonable.

    Returns:
    str: A message indicating the feasibility of the timeline.
    """
    duration_str = duration_str.lower().strip()

    fuzzy_terms = {
        "a few": 3,
        "a couple": 2,
        "several": 6,
        "some": 4,
        "many": 9,
        "a handful": 5
    }

    months = None

    # Check for fuzzy terms like "a few months"
    for fuzzy_word, estimated_num in fuzzy_terms.items():
        if fuzzy_word in duration_str:
            if "week" in duration_str:
                months = estimated_num / 4
            elif "month" in duration_str:
                months = estimated_num
            break

    # Check for ranges like "6-12 months" or "8 to 10 weeks"
    if months is None:
        range_match = re.match(r'(\d+)\s*[-to]+\s*(\d+)\s*(weeks|months)', duration_str)
        single_match = re.match(r'(\d+)\s*(weeks|months)', duration_str)

        try:
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                unit = range_match.group(3)
                avg = (start + end) / 2
                months = avg / 4 if "week" in unit else avg

            elif single_match:
                num = int(single_match.group(1))
                unit = single_match.group(2)
                months = num / 4 if "week" in unit else num
        except:
            return "⚠️ Could not parse timeline value."

    if months is None:
        return "⚠️ Could not understand the timeline. Use phrases like '6 months', '8-12 weeks', or 'a few months'."

    # Evaluate the feasibility
    if months < 3:
        return f"The timeline ({duration_str}) is likely too short for a full migration."
    elif 3 <= months <= 12:
        return f"The timeline ({duration_str}) is potentially feasible depending on complexity."
    else:
        return f"The timeline ({duration_str}) seems reasonable for a full IT migration."


# Tool #4: Search for a term in the entire report
# This tool helps the agent search for a specific term in the entire consulting report.
# It returns the sections where the term was found, if any.

def search_report(term, report_sections):
    """
    Searches for a specific term in the entire consulting report.

    Purpose:
    This function helps the agent search for a specific term in the entire consulting report and returns the sections where the term was found, if any.

    Parameters:
    term (str): The term to search for in the report.
    report_sections (dict): A dictionary where keys are section headers and values are the corresponding section contents.

    Workflow:
    1. Initializes an empty list `found_in` to store the sections where the term is found.
    2. Iterates through each section in the `report_sections` dictionary.
    3. For each section, checks if the term (case-insensitive) is present in the section content.
    4. If the term is found, appends the section header to the `found_in` list.
    5. After checking all sections, returns a message indicating the sections where the term was found or a message indicating that the term was not found.

    Returns:
    str: A message indicating the sections where the term was found or a message indicating that the term was not found.
    """
    found_in = []
    for section, content in report_sections.items():
        if term.lower() in content.lower():
            found_in.append(section)
    if found_in:
        return f"The term '{term}' was found in: {', '.join(found_in)}."
    else:
        return f"The term '{term}' was NOT found anywhere in the report."


# Tool to check report has expected sections
def highlight_missing_sections(report_sections):
    """
    Compares expected canonical (standard) sections against the actual report_sections keys.
    Returns a list of missing expected sections.
    """
    expected_sections = set(canonical_section_map.keys())
    present_sections = set(report_sections.keys())
    
    missing = expected_sections - present_sections
    if missing:
        return "🚨 Missing sections:\n" + "\n".join(f"- {s}" for s in sorted(missing))
    else:
        return "✅ All expected sections are present."


# Tool to check alignment between section and report goals
def check_alignment_with_goals(section_name, report_sections_dict, model="gpt-3.5-turbo", temperature=0.6):
    """
    Checks the alignment between the goals of the report and a specific section.

    Purpose:
    This function evaluates whether a specific section of the report aligns with the stated goals and objectives. It uses the OpenAI API to generate an evaluation of the alignment.

    Parameters:
    section_name (str): The name of the section to evaluate for alignment.
    report_sections_dict (dict): A dictionary where keys are section headers and values are the corresponding section contents.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.6.

    Workflow:
    1. Tries to find the "Goals & Objectives" section in the report.
    2. If the "Goals & Objectives" section is not found, searches for goals in other sections based on keywords.
    3. Retrieves the text of the specified section to evaluate.
    4. If either the goals or the section text is not found, returns a warning message.
    5. Constructs a prompt for the OpenAI API to evaluate the alignment between the goals and the specified section.
    6. Calls the OpenAI API with tracking to get the evaluation.
    7. Returns the evaluation or an error message if the API call fails.

    Returns:
    str: The evaluation of the alignment between the goals and the specified section, or an error message if the API call fails.
    """
    # Step 1: Try exact match first
    try:
        response = call_openai_with_tracking(messages, model=model, temperature=temperature)
        return response.strip()
    except Exception as e:
        return f"⚠️ Failed to check alignment: {str(e)}"


# Tool to compare two sections of a report for duplication, contradictions, or inconsistencies
# This tool compares two sections of an IT consulting report for duplication, contradictions, or inconsistencies.
# It also notes if one section covers content that the other should include.
def compare_with_other_section(section_a, section_b, report_sections_dict, model="gpt-3.5-turbo", temperature=0.6):
    """
    Compares two sections of an IT consulting report for duplication, contradictions, or inconsistencies.

    Purpose:
    This function compares two specified sections of an IT consulting report to identify any duplication, contradictions, or inconsistencies between them. It also notes if one section covers content that the other should include.

    Parameters:
    section_a (str): The name of the first section to compare.
    section_b (str): The name of the second section to compare.
    report_sections_dict (dict): A dictionary where keys are section headers and values are the corresponding section contents.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.6.

    Workflow:
    1. Retrieves the text of the specified sections from the report_sections_dict.
    2. If either section is not found, returns a warning message.
    3. Constructs a prompt for the OpenAI API to compare the two sections.
    4. Calls the OpenAI API with tracking to get the comparison.
    5. Returns the comparison or an error message if the API call fails.

    Returns:
    str: A summary of the comparison between the two sections, or an error message if the API call fails.
    """
    text_a = report_sections_dict.get(section_a)
    text_b = report_sections_dict.get(section_b)

    if not text_a or not text_b:
        return f"⚠️ One or both sections not found: '{section_a}' or '{section_b}'"

    prompt = (
        f"You are comparing two sections of an IT consulting report.\n"
        f"Identify any duplication, contradictions, or inconsistencies between them.\n"
        f"Also note if one section covers content the other should include.\n\n"
        f"Section A: {section_a}\n{text_a}\n\n"
        f"Section B: {section_b}\n{text_b}\n\n"
        "Provide a 3-5 sentence summary of your comparison:"
    )

    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages, model=model, temperature=temperature)
        return response.strip()
    except Exception as e:
        return f"⚠️ Failed to compare sections: {str(e)}"


# Tool to generate client questions based on a section of a report
def generate_client_questions(section_text, model="gpt-3.5-turbo", temperature=0.6):
    """
    Generates client questions based on a section of an IT strategy report.

    Purpose:
    This function acts as a skeptical client reviewing a section of an IT strategy report and generates 3-5 clarifying or challenging questions based on potential assumptions, unclear terms, or missing context.

    Parameters:
    section_text (str): The text of the section to generate questions for.
    model (str): The model to use for the API call. Default is "gpt-3.5-turbo".
    temperature (float): The sampling temperature to use. Higher values mean the model will take more risks. Default is 0.6.

    Workflow:
    1. Constructs a prompt that instructs the model to act as a skeptical client and generate questions based on the section text.
    2. Creates a list of messages with the constructed prompt.
    3. Calls the OpenAI API with tracking using the call_openai_with_tracking function.
    4. If the API call is successful, returns the generated questions.
    5. If an exception occurs, returns a failure message with the exception details.

    Returns:
    str: The generated questions or a failure message if the API call fails.
    """
    prompt = (
        "You are acting as a skeptical client reviewing the following section of an IT strategy report.\n"
        "Generate 3-5 clarifying or challenging questions the client might ask based on potential assumptions, unclear terms, or missing context.\n\n"
        f"Section:\n{section_text}\n\n"
        "Questions:"
    )

    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages, model=model, temperature=temperature)
        return response.strip()
    except Exception as e:
        return f"⚠️ Failed to generate questions: {str(e)}"
