# prompt_builders.py – Prompt construction & tool hinting

# Helper to construct system + user messages for the reasoning agent
def build_review_prompt(report_text, history=[]):
    """
    Constructs system and user messages for the reasoning agent to review a consulting report.

    Parameters:
    report_text (str): The text of the consulting report to be reviewed.
    history (list): A list of previous messages (optional). Default is an empty list.

    Workflow:
    1. The function creates a system message that sets the context for the reasoning agent.
    2. It then creates a user message containing the consulting report text.
    3. The function combines the system message, the history of previous messages, and the user message into a single list.

    Returns:
    list: A list of message dictionaries, including the system message, any historical messages, and the user message.
    """
    system_msg = {
        "role": "system",
        "content": (
            "You are an experienced IT strategy consultant. "
            "You are reviewing a consulting report for completeness, clarity, risks, and alignment with best practices. "
            "Think step-by-step and identify gaps, ask clarifying questions, or suggest improvements. "
            "Your goal is to provide helpful, critical feedback using your expert knowledge."
        )
    }

    user_msg = {
        "role": "user",
        "content": f"Here is the consulting report to review:\n\n{report_text}"
    }

    return [system_msg] + history + [user_msg]


def build_tool_hints(agent):
    """
    Builds a hint message and a combined list of tools for the ReActConsultantAgent based on the section being reviewed.

    Purpose:
    This function generates a hint message prioritizing tools for the agent to use based on the section being reviewed. It combines primary, optional, and global tools into a sorted list.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the section name being reviewed.

    Workflow:
    1. Maps the section name to its canonical form using the map_section_to_canonical function.
    2. Retrieves the primary and optional tools for the canonical section from the tool_priority_map.
    3. Combines the primary, optional, and global tools into a sorted list.
    4. Constructs a hint message prioritizing the primary, optional, and global tools.
    5. Returns the hint message and the combined list of tools.

    Returns:
    tuple: A tuple containing the hint message (str) and the combined list of tools (list).
    """
    canonical = map_section_to_canonical(agent.section_name)
    priorities = tool_priority_map.get(canonical, {})

    primary = priorities.get("primary", [])
    optional = priorities.get("optional", [])

    combined_tools = sorted(set(primary + optional + global_tools))

    hint = "You may use any tool, but prioritize:\n"
    for tool in primary:
        hint += f"- {tool} ✅ (primary)\n"
    for tool in optional:
        hint += f"- {tool} ◽️ (optional)\n"
    for tool in global_tools:
        if tool not in primary and tool not in optional:
            hint += f"- {tool} 🌐 (global)\n"

    return hint, combined_tools


# Format the tool catalog for display in the prompt for consumption by LLM

def format_tool_catalog_for_prompt(tool_catalog):
    """
    Formats the tool catalog for display in the prompt for consumption by LLM.

    Purpose:
    This function formats the tool catalog into a human-readable string that lists each tool along with its description and usage. This formatted string can be used in prompts for language models to understand the available tools.

    Parameters:
    tool_catalog (dict): A dictionary where keys are tool names and values are dictionaries containing tool metadata, including 'description' and 'usage'.

    Workflow:
    1. Initializes a list with the header "Available tools:".
    2. Iterates through each tool in the tool_catalog dictionary.
    3. For each tool, appends its name, description, and usage to the list.
    4. Joins the list into a single string with newline characters.

    Returns:
    str: A formatted string listing all tools with their descriptions and usage.
    """
    lines = ["\n(You may use these tools if you believe they apply — but prioritize the tools listed above.)\n\n"]
    for tool, meta in tool_catalog.items():
        lines.append(f"- {tool} (v{meta['version']}): {meta['description']}")
        lines.append(f"  Usage: {meta['usage']}")
        if meta.get("examples"):
            for ex in meta["examples"]:
                lines.append(f"  Example: {ex}")
        lines.append("")  # spacing between tools
    return "\n".join(lines)



