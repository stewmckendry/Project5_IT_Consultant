# src/utils/thought_filtering.py

from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from src.models.openai_embeddings import get_openai_embedding
from src.utils.logging_utils import log_phase

def filter_redundant_thoughts(
    new_thoughts: List[str],
    prev_thoughts: List[str],
    prev_embeddings: List[List[float]],
    threshold: float = 0.85
) -> Tuple[List[str], List[List[float]]]:
    """
    Filters out redundant thoughts based on similarity to previous thoughts.
    
    Returns only novel thoughts and their embeddings.
    """
    if not prev_thoughts:
        new_embeddings = [get_openai_embedding(t) for t in new_thoughts]
        return new_thoughts, new_embeddings

    novel_thoughts = []
    novel_embeddings = []

    for t in new_thoughts:
        emb = get_cached_embedding(t, get_openai_embedding)
        sims = cosine_similarity([emb], prev_embeddings)[0]
        if max(sims, default=0) < threshold:
            novel_thoughts.append(t)
            novel_embeddings.append(emb)

    return novel_thoughts, novel_embeddings


embedding_cache = {}
embedding_cache_stats = {
    "hits": 0,
    "misses": 0
}

def get_cached_embedding(text, get_embedding_fn):
    global embedding_cache
    if text in embedding_cache:
        embedding_cache_stats["hits"] += 1
        log_phase(f"🧠 Embedding cache hit: {text}")
        return embedding_cache[text]
    embedding = get_embedding_fn(text)
    embedding_cache[text] = embedding
    embedding_cache_stats["misses"] += 1
    log_phase(f"🧠 Embedding cache miss: {text}")
    return embedding

def reset_embedding_cache():
    global embedding_cache
    embedding_cache.clear()
    embedding_cache_stats["hits"] = 0
    embedding_cache_stats["misses"] = 0

def get_embedding_cache_stats():
    return embedding_cache_stats.copy()
