import pytest
from src.models.tot_agent import TreeNode, SimpleToTAgent

def test_tree_node_path_traversal():
    root = TreeNode("ROOT")
    child1 = TreeNode("Thought A", parent=root)
    child2 = TreeNode("Thought B", parent=child1)

    path = child2.path()
    assert path == ["ROOT", "Thought A", "Thought B"]

def test_simple_tot_agent_run_returns_reasoning_path():
    # Mock LLM that always returns the same 3 thoughts
    def mock_llm(prompt):
        return "1. Thought A\n2. Thought B\n3. Thought C"

    # Mock scorer that gives descending scores based on thought content
    def mock_scorer(thought):
        return {"Thought A": 7, "Thought B": 9, "Thought C": 5}.get(thought, 1)

    agent = SimpleToTAgent(llm=mock_llm, scorer=mock_scorer, beam_width=2, max_depth=2)

    section = "Sample proposal section about agile delivery."
    criterion = "Delivery Approach"

    result = agent.run(section, criterion)

    assert "criterion" in result
    assert "score" in result
    assert "reasoning_path" in result
    assert isinstance(result["reasoning_path"], list)
    assert result["score"] in [7, 9, 5]

def test_simple_tot_agent_handles_empty_thoughts_gracefully():
    def mock_llm(prompt):
        return ""

    def mock_scorer(thought):
        return 5

    agent = SimpleToTAgent(llm=mock_llm, scorer=mock_scorer, beam_width=2, max_depth=2)

    section = "Content doesn't matter"
    criterion = "Something"

    result = agent.run(section, criterion)

    assert result["score"] == 0
    assert "No valid thoughts" in result["reasoning_path"][0]
