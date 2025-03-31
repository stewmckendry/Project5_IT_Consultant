# Recommend tools for ReActConsultant Agent based on the RFP evaluation criterion

from src.utils.tools.tool_embeddings import suggest_tools_by_embedding
from src.utils.tools.tool_catalog_RFP import tool_catalog  # or however it's defined
#from src.utils.text_processing import truncate_text  # optional, if needed
from src.utils.tools.tool_catalog import tool_priority_map, global_tools, criterion_tool_map
from src.server.prompt_builders import format_tool_hints_for_prompt

def build_tool_hint_text_forRFPeval(criterion):
    """
    Returns a tool hint text based on the RFP evaluation criterion to help the LLM prioritize relevant tools.
    """
    tools = criterion_tool_map.get(criterion, [])
    if not tools:
        return "No prioritized tools. Use your judgment."

    lines = []
    for tool in tools:
        info = tool_catalog.get(tool, {})
        lines.append(f"- **{tool}**: {info.get('description', 'No description')}")
    return "\n".join(lines)


def build_tool_hints_for_rfp_eval_embedding(criterion, proposal_text, thoughts=None, tool_embeddings=None, top_n=5):
    """
    Generate a prioritized tool list based on embeddings, using the criterion + proposal + ToT thoughts.
    """
    if tool_embeddings is None:
        raise ValueError("❌ Must provide tool_embeddings.")

    # Build input text for similarity
    thought_text = "\n".join(thoughts) if thoughts else ""
    query = f"Criterion: {criterion}\n\nTop Thoughts:\n{thought_text}"

    # Optionally truncate if it's very long (OpenAI embedding limit ~8192 tokens)
    #query = truncate_text(query, max_chars=4000)

    # Get top matching tools
    ranked_tools = suggest_tools_by_embedding(query, tool_embeddings, top_n=top_n)

    # Format as tool hint block
    hint_text = format_tool_hints_for_prompt(ranked_tools, tool_catalog)

    return hint_text, [tool_name for tool_name, _ in ranked_tools]
