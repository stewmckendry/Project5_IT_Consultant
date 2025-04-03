from typing import Dict, List, Tuple
from src.utils.tools.tool_catalog_RFP import tool_catalog
from src.utils.logging_utils import log_phase


def get_relevant_tools(
    criterion: str,
    section_text: str,
    tool_embeddings: Dict[str, List[float]],
    similarity_threshold: float = 0.75,
    query_embedding: List[float] = None,
    return_with_scores: bool = True,
    verbose: bool = False,
    filter_sections: List[str] = None
) -> List[Tuple[str, float]] | List[str]:
    """
    Returns relevant tools for a criterion based on semantic similarity above a threshold.

    Parameters:
        criterion (str): Evaluation criterion (e.g., "Solution Fit").
        section_text (str): Section text from proposal.
        tool_embeddings (Dict): Precomputed OpenAI embeddings for tools.
        similarity_threshold (float): Cosine similarity threshold (0.0 to 1.0).
        query_embedding (List[float], optional): Pass this to avoid recomputing the query embedding.
        return_with_scores (bool): If True, return (tool_name, similarity) tuples.
        verbose (bool): If True, log matches and scores.

    Returns:
        List[str] or List[Tuple[str, float]]
    """
    from src.models.openai_embeddings import get_openai_embedding
    from sklearn.metrics.pairwise import cosine_similarity
    from src.utils.logging_utils import logger

    log_phase(f"🔍 Finding relevant tools for '{criterion}'...")

    if not query_embedding:
        query = f"{criterion}: {section_text}"
        query_embedding = get_openai_embedding(query)
        log_phase(f"✅ Query embedding computed for '{criterion}'.")
        log_phase(f"Query: {query}")

    matches = []

    for tool_name, tool_emb in tool_embeddings.items():
        # Optional section filtering
        tool_meta = tool_catalog.get(tool_name, {})
        if filter_sections and tool_meta.get("section") not in filter_sections:
            continue
        # Calculate cosine similarity
        try:
            score = round(cosine_similarity([query_embedding], [tool_emb])[0][0], 3)
            log_phase(f"🔍 Tool: {tool_name} → score={score:.3f}")
            if score >= similarity_threshold:
                matches.append((tool_name, score))
                if verbose:
                    logger.debug(f"🔍 Relevant tool match: {tool_name} → score={score:.3f}")
        except Exception as e:
            if verbose:
                logger.error(f"❌ Error calculating similarity for '{tool_name}': {e}")
            continue  # Ensure failure of one tool doesn't interrupt rest

    matches.sort(key=lambda x: x[1], reverse=True)

    return matches if return_with_scores else [tool for tool, _ in matches]


def group_tools_by_section(tool_catalog):
    grouped = {}
    for tool_name, meta in tool_catalog.items():
        section = meta.get("section", "Uncategorized")
        grouped.setdefault(section, []).append(tool_name)
    return grouped
