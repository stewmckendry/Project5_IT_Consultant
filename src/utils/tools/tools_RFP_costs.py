from src.models.openai_interface import call_openai_with_tracking
from src.server.prompt_builders import build_dual_context_prompt

def check_value_for_money(agent) -> str:
    """
    Checks whether the proposed cost offers good value for the services and capabilities described.
    """
    instructions = (
        "Evaluate whether the cost described appears to offer good value for the services and features provided. "
        "Is the price appropriate for the scope and quality of the offering?\n\n"
        "Explain your reasoning based on best practices and common expectations for similar proposals.\n\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    try:
        response = call_openai_with_tracking(prompt)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def check_cost_benchmark(agent) -> str:
    """
    Benchmarks the provided cost against typical pricing in the industry, if possible.
    """
    instructions = (
        "Based on your knowledge of industry norms and typical vendor pricing, is the proposed cost "
        "within a reasonable range? Mention whether it appears high, low, or typical compared to similar offerings.\n\n"
        "Explain your reasoning based on benchmarks, market trends, or comparable services.\n\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    try:
        response = call_openai_with_tracking(prompt)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


def generate_cost_forecast(agent) -> str:
    """
    Forecasts potential long-term or total costs based on the provided pricing structure and risk factors.
    """
    instructions = (
        "Based on the pricing model and assumptions described, forecast the likely total cost over the full term "
        "of the agreement. Consider any risk factors, missing details, or cost escalation possibilities. "
        "Mention if costs may vary based on user volume, modules selected, or client-provided responsibilities.\n\n"
        "Explain your reasoning.\n\n"
    )
    prompt = build_dual_context_prompt(instructions, agent)
    try:
        response = call_openai_with_tracking(prompt)
        return response.strip()
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"


