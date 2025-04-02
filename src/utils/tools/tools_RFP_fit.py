from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt

def evaluate_product_fit(agent, input_arg) -> str:
    """
    Checks how well the product functionality aligns with the requirements.
    """
    instructions = (
        "Evaluate how well the product functionality described aligns with the client’s requirements. "
        "Look for strong matches, partial gaps, or generic responses. Focus on how specifically it addresses key needs.\n\n"
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
    
def evaluate_nfr_support(agent, input_arg) -> str:
    """
    Evaluates support for non-functional requirements (NFRs): privacy, security, accessibility, UX, etc.
    """
    instructions = (
        "Does the proposal demonstrate strong support for non-functional requirements (NFRs), including privacy, security, "
        "accessibility, user experience, performance, and availability? Identify any strengths or gaps.\n\n"
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

def evaluate_modularity_and_scalability(agent, input_arg) -> str:
    """
    Evaluates if the solution is modular and scalable across business lines.
    """
    instructions = (
        "Evaluate how modular and scalable the solution is. Can modules be added, removed, or configured without extensive "
        "customization? Is it designed to support scaling across multiple business lines?\n\n"
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


def check_product_roadmap(agent, input_arg) -> str:
    """
    Checks if the proposal includes a product roadmap aligned with client needs and long-term evolution.
    """
    instructions = (
        "Does the proposal include a product roadmap? Does it show a clear future direction and investment strategy that "
        "aligns with the client’s evolving needs?\n\n"
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


def evaluate_demos_and_proofs(agent, input_arg) -> str:
    """
    Checks for demos, case studies, pilots, or outcomes that support product claims.
    """
    instructions = (
        "Does the proposal include any demos, case studies, pilots, or proven results that support claims about product quality "
        "and fit? Consider client examples, metrics, or third-party validation.\n\n"
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

