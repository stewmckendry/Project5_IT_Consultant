# tools_nlp.py – Language-level NLP tools

# Tool to check for jargon or technical terms in a section

JARGON_LIST = {
    "synergy", "leverage", "optimize", "stakeholder alignment", "enablement",
    "digital transformation", "bandwidth", "scalability", "paradigm",
    "blockchain", "AI", "ML", "IoT", "Zero Trust", "DevOps", "infrastructure-as-code",
    "EHR", "CRM", "VPN", "cloud-native", "containerization", "agile methodology"
}

def check_for_jargon(section_text):
    """
    Checks for jargon or technical terms in a section of the report.

    Purpose:
    This function helps identify the presence of jargon or technical terms in a section of the report by searching for predefined terms.

    Parameters:
    section_text (str): The text of the section to search within.

    Workflow:
    1. Initializes an empty list `found_terms` to store the jargon or technical terms found in the section.
    2. Iterates through each term in the `JARGON_LIST` set.
    3. For each term, constructs a regex pattern to match the term as a whole word (case-insensitive).
    4. Searches for the term in the section text using the regex pattern.
    5. If the term is found, appends it to the `found_terms` list.
    6. After checking all terms, returns a message indicating the jargon or technical terms found or a message indicating that no notable jargon or technical terms were found.

    Returns:
    str: A message indicating the jargon or technical terms found in the section, or a message indicating that no notable jargon or technical terms were found.
    """
    found_terms = []
    for term in JARGON_LIST:
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, section_text, flags=re.IGNORECASE):
            found_terms.append(term)
    if found_terms:
        return f"The section includes jargon or technical terms: {', '.join(found_terms)}."
    else:
        return "No notable jargon or technical terms found."

# Tool to assess readability of a section with textstat scores
# Flesch Reading Ease: higher score indicates easier readability
# Reading Level Estimate: grade level of text
# Difficult Words Count: number of difficult words in the text
def check_readability(section_text):
    score = textstat.flesch_reading_ease(section_text)
    level = textstat.text_standard(section_text)
    difficult = textstat.difficult_words(section_text)

    summary = (
        f"📖 **Flesch Reading Ease**: {score:.1f} (higher = easier)\n"
        f"🏫 **Reading Level Estimate**: {level}\n"
        f"🧠 **Difficult Words Count**: {difficult}"
    )
    return summary


def analyze_tone_textblob(section_text):
    """
    Analyzes the tone and clarity of a given text section using TextBlob.

    Purpose:
    This function uses the TextBlob library to analyze the sentiment of a given text section. It determines the tone (positive, neutral, or negative) based on the polarity score and the clarity (objective or subjective) based on the subjectivity score.

    Parameters:
    section_text (str): The text of the section to be analyzed.

    Workflow:
    1. Creates a TextBlob object from the section text.
    2. Extracts the polarity and subjectivity scores from the TextBlob object.
    3. Determines the tone based on the polarity score:
       - If polarity > 0.2, the tone is positive.
       - If polarity < -0.2, the tone is negative.
       - Otherwise, the tone is neutral.
    4. Determines the clarity based on the subjectivity score:
       - If subjectivity < 0.4, the clarity is objective.
       - Otherwise, the clarity is subjective.
    5. Returns a formatted string with the tone and clarity information.

    Returns:
    str: A formatted string indicating the tone and clarity of the text, including the polarity and subjectivity scores.
    """
    blob = TextBlob(section_text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    tone = "neutral"
    if polarity > 0.2:
        tone = "positive"
    elif polarity < -0.2:
        tone = "negative"

    clarity = "objective" if subjectivity < 0.4 else "subjective"

    return (
        f"💬 **Tone**: {tone} (polarity: {polarity:.2f})\n"
        f"🧠 **Clarity**: {clarity} (subjectivity: {subjectivity:.2f})"
    )


def extract_named_entities(section_text):
    """
    Extracts named entities from a given text section using a preloaded NLP model.

    Purpose:
    This function analyzes a text section to identify named entities (e.g., persons, organizations, dates) and categorizes them by their entity type. It provides a summary of the detected entities, grouped by their labels.

    Parameters:
    section_text (str): The text of the section to be analyzed for named entities.

    Workflow:
    1. Processes the input text using the preloaded NLP model (`nlp`).
    2. Checks if any named entities are detected in the text.
       - If no entities are found, returns a message indicating no named entities were detected.
    3. Iterates through the detected entities and groups them by their labels (e.g., PERSON, ORG, DATE).
    4. Removes duplicate entities within each label and limits the output to the first 5 unique entities per label.
    5. Constructs a formatted summary of the detected entities, grouped by their labels.

    Returns:
    str: A formatted string summarizing the detected named entities, grouped by their labels. If no entities are found, returns a message indicating this.
    """
    doc = nlp(section_text)
    if not doc.ents:
        return "No named entities found."

    entity_summary = {}
    for ent in doc.ents:
        label = ent.label_
        entity_summary.setdefault(label, []).append(ent.text)

    result = "🧾 **Named Entities Detected:**\n"
    for label, values in entity_summary.items():
        unique_vals = list(set(values))
        result += f"- **{label}**: {', '.join(unique_vals[:5])}\n"

    return result
