import os
import pickle
import numpy as np
import tempfile
import pytest
from unittest.mock import patch

from src.utils.tools.tool_embeddings import build_tool_embeddings, suggest_tools_by_embedding

# Dummy tool catalog
dummy_tool_catalog = {
    "tool_a": {
        "description": "Checks alignment with strategic goals.",
        "examples": ["evaluate if proposal aligns with public health objectives."]
    },
    "tool_b": {
        "description": "Analyzes cost breakdown and pricing clarity.",
        "examples": ["check if price includes support and training."]
    }
}

# Create dummy embeddings (vector length = 3 for simplicity)
dummy_embeddings = {
    "tool_a": np.array([0.1, 0.2, 0.3]),
    "tool_b": np.array([0.4, 0.5, 0.6])
}


@patch("src.utils.tools.tool_embeddings.get_openai_embedding")
def test_build_tool_embeddings_creates_and_caches(mock_get_embedding):
    mock_get_embedding.return_value = np.array([0.1, 0.2, 0.3])

    with tempfile.TemporaryDirectory() as temp_dir:
        cache_path = os.path.join(temp_dir, "embeddings.pkl")
        embeddings = build_tool_embeddings(dummy_tool_catalog, cache_path=cache_path)

        assert "tool_a" in embeddings
        assert os.path.exists(cache_path)

        # Confirm it loaded from cache on second call
        mock_get_embedding.reset_mock()
        _ = build_tool_embeddings(dummy_tool_catalog, cache_path=cache_path)
        mock_get_embedding.assert_not_called()


@patch("src.utils.tools.tool_embeddings.get_openai_embedding")
def test_suggest_tools_by_embedding_returns_sorted_matches(mock_get_embedding):
    # Mock embedding for query: similar to tool_b; x is the query passed to get_openai_embedding (or mock_get_embedding for this stub)
    mock_get_embedding.side_effect = lambda x: np.array([0.4, 0.5, 0.6]) if "price" in x else np.array([0.1, 0.2, 0.3])

    query = "Does the price include training?"
    result = suggest_tools_by_embedding(query, dummy_embeddings, top_n=2)

    assert len(result) == 2
    assert result[0][0] == "tool_b"  # Highest similarity
    assert isinstance(result[0][1], float)
