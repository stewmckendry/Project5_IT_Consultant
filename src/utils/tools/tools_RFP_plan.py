from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt

def check_implementation_milestones(agent, input_arg) -> str:
    """
    Checks if the proposal outlines clear implementation milestones or phases.
    """
    instructions = (
        "Review the following section and determine if the proposal clearly defines implementation milestones or phases. "
        "Look for named phases (e.g., Discovery, Design, Build), target dates, or sequencing of deliverables. "
        "Explain your reasoning based on best practices and common delivery milestones.  Explain impact of missing milestones.\n\n"
        "Query: "
        f"{input_arg}\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"

def check_resource_plan_realism(agent, input_arg) -> str:
    """
    Evaluates whether the proposed staffing and resource plan appears realistic for the scope of work.
    """
    instructions = (
        "Analyze the section below to determine whether the vendor's proposed resource plan is realistic. "
        "Consider the number and roles of team members, the timeline, scope of deliverables, and any stated assumptions. "
        "Query: "
        f"{input_arg}\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"

def check_assumption_reasonableness(agent, input_arg) -> str:
    """
    Evaluates whether the assumptions in the implementation plan are reasonable and realistic.
    """
    instructions = (
        "Evaluate the following section to identify any stated assumptions. "
        "Assess whether each assumption is reasonable and realistic based on typical project delivery practices. "
        "Query: "
        f"{input_arg}\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_timeline_feasibility(agent, input_arg) -> str:
    """
    Evaluates whether the assumptions in the implementation plan are reasonable and realistic.
    """
    instructions = (
        "Assess the following text which describes a project implementation timeline. "
        "Determine whether this timeline is realistic for a complex IT implementation. "
        "Query: "
        f"{input_arg}\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"

def check_contingency_plans(agent, input_arg) -> str:
    """
    Evaluates if the proposal includes contingency plans or risk mitigation strategies.
    """
    instructions = (
        "Review the section below and determine whether the vendor has outlined contingency plans "
        "or fallback strategies to address risks or delays during implementation. "
        "Highlight any gaps if no such plans are found. "
        "Query: "
        f"{input_arg}\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"
