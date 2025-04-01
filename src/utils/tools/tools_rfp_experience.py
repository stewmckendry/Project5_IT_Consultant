from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt

def check_vendor_experience_relevance(agent) -> str:
    """
    Evaluates if the vendor demonstrates relevant experience with projects of similar scope, scale, or sector.
    """
    instructions = (
        "Evaluate the following proposal section to determine if the vendor has prior experience delivering "
        "solutions of similar scope, size, complexity, or in a similar domain (e.g., healthcare, government). "
        "Look for named clients, project descriptions, and relevance to the RFP context.\n\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_vendor_experience_evidence(agent) -> str:
    """
    Evaluates if the vendor demonstrates relevant experience with projects of similar scope, scale, or sector.
    """
    instructions = (
        "Review the following section and determine if the vendor's claimed experience is supported by specific evidence. "
        "Look for named clients, case studies, outcome metrics, or references to support their past success.\n\n"
        f"Section:\n{text}"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"
