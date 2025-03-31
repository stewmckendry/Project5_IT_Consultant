# tools_nlp.py – Language-level NLP tools

# Tool to check for jargon or technical terms in a section

import re
from textstat.textstat import textstat
import spacy
from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt


def check_for_jargon(agent) -> str:
    """
    Uses an LLM to analyze if the section overuses jargon or buzzwords that might reduce clarity.
    """
    prompt = build_dual_context_prompt(
        "Identify any jargon, marketing buzzwords, or overly technical terms that may obscure meaning or reduce clarity. "
        "List the terms and briefly explain if they hinder understanding or appear unnecessary.",
        agent
    )

    try:
        response = call_openai_with_tracking(prompt)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


# Tool to assess readability of a section with textstat scores
# Flesch Reading Ease: higher score indicates easier readability
# Reading Level Estimate: grade level of text
# Difficult Words Count: number of difficult words in the text
def check_readability(agent):
    full_proposal_text = agent.full_proposal_text
    score = textstat.flesch_reading_ease(full_proposal_text)
    level = textstat.text_standard(full_proposal_text)
    difficult = textstat.difficult_words(full_proposal_text)

    summary = (
        f"📖 **Flesch Reading Ease**: {score:.1f} (higher = easier)\n"
        f"🏫 **Reading Level Estimate**: {level}\n"
        f"🧠 **Difficult Words Count**: {difficult}"
    )
    return summary


def analyze_tone_textblob(agent):
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
    full_proposal_text = agent.full_proposal_text
    blob = TextBlob(full_proposal_text)
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

# Load the spaCy NLP model
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(agent):
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
    proposal_text = agent.full_proposal_text
    doc = nlp(proposal_text)
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
