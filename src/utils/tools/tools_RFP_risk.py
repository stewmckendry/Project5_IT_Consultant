from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt

def check_data_privacy_and_security_measures(agent, input_arg) -> str:
    """
    Checks whether the proposal includes clear and adequate data privacy and security protections.
    """
    instructions = (
        "Does the proposal include specific and adequate protections for data privacy and security? "
        "Mention encryption, access control, compliance with HIPAA/GDPR/PHIPA, and cloud standards.\n\n"
        "Query: "
        f"{input_arg}\n\n"
        "------------------\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_risk_register_or_mitigation_plan(agent, input_arg) -> str:
    """
    Checks whether a formal risk register or mitigation plan is included and appropriate.
    """
    instructions = (
        "Does the proposal include a formal risk register or risk mitigation plan? "
        "Evaluate whether risks are clearly identified and paired with mitigation strategies.\n\n"
        "Query: "
        f"{input_arg}\n\n"
        "------------------\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_compliance_certifications(agent, input_arg) -> str:
    """
    Checks for the presence of relevant compliance certifications (ISO, SOC 2, HIPAA, etc.).
    """
    instructions = (
        "Does the proposal include references to relevant compliance certifications or attestations "
        "(e.g., ISO 27001, SOC 2, HIPAA, PHIPA)? Are these certifications current and credible?\n\n"
        "Query: "
        f"{input_arg}\n\n"
        "------------------\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


