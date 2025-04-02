from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt

def check_team_experience_alignment(agent, input_arg) -> str:
    instructions = f"""
You are reviewing a proposal section describing the proposed team.

Evaluate how well the team's experience aligns with the requirements of the project. Check whether the CVs and team roles demonstrate relevant skills and experience (e.g., similar projects, domain knowledge, certifications).

For each named resource, also check external sources on web or LinkedIn to verify their experience.

Query: 
{input_arg}

-------------
"""
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def detect_bait_and_switch_risk(agent, input_arg) -> str:
    instructions = f"""
Review the following proposal section and determine if there's a risk of "bait and switch"—i.e., proposing senior or high-quality staff during the bid but not committing to actually staffing them.

Look for vague staffing commitments, lack of CV details, or hedging language.

Query: 
{input_arg}

-------------
"""
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"
    

def check_local_resource_presence(agent, input_arg) -> str:
    instructions = f"""
You're reviewing a proposal section to assess whether the vendor proposes using local, on-site, or regionally based staff.

Extract any relevant details about staffing location and evaluate whether this meets the needs of the client.

Query: 
{input_arg}

-------------
"""
    prompt = build_dual_context_prompt(instructions, agent)
    messages = [{"role": "user", "content": prompt}]
    try:
        response = call_openai_with_tracking(messages)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"

