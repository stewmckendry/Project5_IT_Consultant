# Use embeddings to recommend tools that are most relevant to the proposal content.

from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from src.models.openai_embeddings import get_openai_embedding

import os
import pickle
from src.models.openai_embeddings import get_openai_embedding

# Convert tool catalog into embeddings (one for each tool)
# Cache for future use
def build_tool_embeddings(tool_catalog, cache_path="tool_embeddings_cache.pkl"):
    # If cached, load from file
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            print("✅ Loaded cached tool embeddings.")
            return pickle.load(f)

    # Otherwise, generate and cache
    print("⚙️ Generating tool embeddings...")
    tool_embeddings = {}
    for name, meta in tool_catalog.items():
        text = meta["description"] + " " + " ".join(meta["examples"])
        embedding = get_openai_embedding(text)
        tool_embeddings[name] = embedding

    with open(cache_path, "wb") as f:
        pickle.dump(tool_embeddings, f)
        print(f"✅ Saved embeddings to: {cache_path}")

    return tool_embeddings


# Main function to get top-N matches
def suggest_tools_by_embedding(query, tool_embeddings, top_n=5):
    query_embedding = get_openai_embedding(query)
    scores = {
        tool: cosine_similarity([query_embedding], [embed])[0][0]
        for tool, embed in tool_embeddings.items()
    }
    top_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return top_matches
