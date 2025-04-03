from src.models.openai_interface import call_openai_with_tracking
from src.utils.tools.tools_web import search_external_sources
from src.server.prompt_builders import build_dual_context_prompt
import re

def detect_boilerplate_or_marketing_fluff(agent, input_arg) -> str:
    """
    Uses LLM to detect boilerplate or marketing-heavy language in a section.
    
    Asks the LLM to evaluate whether the text sounds vague, generic, or overly promotional.
    Returns a short diagnostic message.

    Parameters:
    section_text (str): The section text to evaluate.

    Returns:
    str: Diagnostic message indicating whether marketing fluff is present.
    """
    instructions = f"""
You are an expert proposal evaluator.

Carefully read the following section and assess whether it contains boilerplate or marketing-heavy language. 
Specifically, identify vague, generic, or promotional phrasing that does not contribute concrete value or insight.

If any is found, list examples and suggest areas for improvement.
If the section is clear and substantive, confirm that.

Query: {input_arg}
"""
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages, model="gpt-3.5-turbo")
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def evaluate_writing_clarity(agent, input_arg) -> str:
    instructions = f"""
You are an expert editor helping assess a vendor's proposal writing.

Evaluate the following section for:
1. Clarity — Is the meaning obvious, or are there ambiguous/confusing phrases?
2. Conciseness — Is there unnecessary repetition or wordiness?
3. Readability — Is it written in a straightforward, easy-to-follow way?

Return a 2-3 sentence critique of the writing quality.

Query: {input_arg}
"""
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_fact_substantiation(agent, input_arg) -> str:
    section_text = agent.section_text
    full_proposal_text = agent.full_proposal_text
    summary_text = summarize_to_query(section_text)
    external_evidence = search_external_sources(summary_text)  # use first 200 chars as topic summary
    prompt = f"""
You are a fact-checking assistant evaluating a vendor proposal section.

Analyze whether the claims in the following text are:
- Substantiated (supported by evidence, examples, numbers, or named clients)
- Or vague/unsupported (marketing-style claims with no details)

Return a short summary indicating which parts are substantiated and which are not.

Query:
{input_arg}

_________________

Section:
{section_text}

------------------

Full Proposal Context:
{full_proposal_text}

------------------

Below is some external context from web/wikipedia/academic sources:

{external_evidence}

Please evaluate whether the statement appears factually supported and identify anything that may be unverifiable, exaggerated, or vague.
"""
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_for_unsupported_assumptions(agent, input_arg) -> str:
    section_text = agent.section_text
    full_proposal_text = agent.full_proposal_text
    summary_text = summarize_to_query(section_text)  # corrected variable name
    external_evidence = search_external_sources(summary_text)  # use first 200 chars as topic summary
    prompt = f"""
You are reviewing a vendor proposal for unsupported or unrealistic assumptions.

Analyze the section below and identify:
1. Any implicit or explicit assumptions
2. Whether they are realistic or risky
3. Any concerns the client might have

Return your findings in bullet points.

Query:
{input_arg}
_________________

Section:
{section_text}

------------------

Full Proposal Context:
{full_proposal_text}

------------------

Below is some external context from web/wikipedia/academic sources:

{external_evidence}

Please evaluate whether the assumptions appear realistic and any concerns the client might have.

"""
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"
    


def summarize_to_query(text: str, max_chars: int = 200) -> str:
    """
    Summarizes a longer text block into a compact query for external search.
    """
    prompt = f"""
You are helping generate a focused search query for fact-checking or validation.

Here is the full text:
{text}

Please summarize this into a concise search query or fact-checking topic. Keep it under {max_chars} characters, preserving the core claim or topic to investigate.
"""
    messages = [{"role": "user", "content": prompt}]
    try:
        result = call_openai_with_tracking(messages, model="gpt-3.5-turbo")
        return result.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def extract_tool_name(action_str):
    """
    Extracts the tool name from a string like `tool_name["arg"]`.
    Returns original string if no brackets found.
    """
    match = re.match(r"^([a-zA-Z0-9_]+)", action_str)
    return match.group(1) if match else action_str