from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt

def evaluate_collaboration_approach(agent, input_arg) -> str:
    instructions = f"""
You are reviewing a proposal's section on team or collaboration.

Evaluate whether the approach promotes a strong partnership with the client. Look for:
- Role clarity between vendor and client
- Communication approach
- Collaboration tools or cadences
- Tone (cooperative or rigid)

Return a 2-3 sentence evaluation.

Query: {input_arg}
------------------
"""
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_discovery_approach(agent, input_arg) -> str:
    """
    Evaluates whether the vendor has a clear and effective approach for the Discovery phase.
    """
    instructions = (
        "Evaluate the following methodology section. Focus on how the vendor handles the Discovery phase. "
        "Does their approach identify objectives, current state, stakeholders, constraints, and early risks? "
        "Is it structured and compatible with government or enterprise expectations? "
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


def check_requirements_approach(agent, input_arg) -> str:
    """
    Evaluates whether the vendor has a clear and effective approach for the Discovery phase.
    """
    instructions = (
        "Review the vendor's methodology for the Requirements phase. "
        "Does it describe how business, functional, and non-functional requirements will be gathered? "
        "Are multiple stakeholder perspectives included? Is traceability or documentation mentioned? "
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


def check_design_approach(agent, input_arg) -> str:
    """
    Evaluates whether the vendor has a clear and effective approach for the Discovery phase.
    """
    instructions = (
        "Analyze the vendor’s design phase approach. Does it involve architectural design, UX/UI prototyping, "
        "integration planning, and alignment with client standards or enterprise architecture? "
        "Does it consider agile or iterative design and involve the client? "
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


def check_build_approach(agent, input_arg) -> str:
    """
    Evaluates whether the vendor has a clear and effective approach for the Design phase.
    """
    instructions = (
        "Evaluate the Build phase of the vendor’s methodology. "
        "Does it describe development approach (e.g., agile sprints, DevOps), use of reusable components, "
        "code quality checks, documentation, and security integration?\n\n"
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

def check_test_approach(agent, input_arg) -> str:
    """
    Evaluates the vendor’s testing methodology and practices.
    """
    instructions = (
        "Analyze the vendor’s approach to testing. Does it include types of tests (unit, integration, UAT), "
        "test data strategy, automation tools, accessibility and performance testing, and issue management? "
        "Is the client involved in test planning or execution?\n\n"
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


def check_deployment_approach(agent, input_arg) -> str:
    """
    Evaluates the vendor’s deployment approach and readiness strategy.
    """
    instructions = (
        "Evaluate the Deployment phase of the vendor’s methodology. Does it include cutover strategy, go/no-go criteria, "
        "rollback plans, stakeholder communication, and readiness validation?\n\n"
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


def check_operate_approach(agent, input_arg) -> str:
    """
    Evaluates the vendor’s approach to operations, sustainment, and continuous improvement.
    """
    instructions = (
        "Evaluate the Operate phase of the vendor’s methodology. Does it include support model, SLAs, incident management, "
        "monitoring, feedback loops, and continuous improvement practices?\n\n"
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


def check_agile_compatibility(agent, input_arg) -> str:
    """
    Checks whether the vendor's use of agile is structured and compatible with client needs,
    including things like agile with fixed price or hybrid models.
    """
    prompt = (
        "Evaluate the vendor's use of Agile in their delivery methodology. "
        "Is Agile used in a structured and disciplined way? Does it integrate with client governance models? "
        "Is it compatible with fixed-price contracts or evolving scope? "
        "Does the approach help achieve cost and time certainty?\n\n"
        "Query: "
        f"{input_arg}\n\n"
        "------------------\n"
    )
    prompt = build_dual_context_prompt(prompt, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_accelerators_and_tools(agent, input_arg) -> str:
    """
    Evaluates whether the vendor includes accelerators, templates, or proprietary tools
    to improve speed, consistency, or quality of delivery.
    """
    instructions = (
        "Does the vendor describe use of accelerators, pre-built assets, templates, or proprietary tools "
        "to improve delivery speed, reduce effort, ensure quality, or integrate with client systems? "
        "How do these tools contribute to the project outcomes?\n\n"
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
