import pytest
from unittest.mock import patch
from src.models.llmscoring_rfp import score_proposal_content_with_llm_and_tools


@patch("src.models.llmscoring_rfp.call_openai_with_tracking")
def test_score_proposal_with_valid_response(mock_call_openai):
    mock_call_openai.return_value = (
        "Score: 8\n"
        "Explanation: The proposal addresses the criterion in detail, offering strong examples."
    )

    proposal = "This is a vendor proposal about adaptability and integration."
    criterion = "Solution Fit"
    thoughts = ["Aligns with team goals", "Covers integration edge cases"]
    tools = [{"tool": "solution_checker", "result": "Comprehensive feature match"}]

    score, explanation = score_proposal_content_with_llm_and_tools(
        proposal, criterion, top_thoughts=thoughts, triggered_tools=tools
    )

    assert score == 8
    assert "addresses the criterion" in explanation
    mock_call_openai.assert_called_once()


@patch("src.models.llmscoring_rfp.call_openai_with_tracking")
def test_score_proposal_with_malformed_response(mock_call_openai):
    mock_call_openai.return_value = "This is not in the expected format."

    score, explanation = score_proposal_content_with_llm_and_tools(
        proposal="Some text",
        criterion="Clarity"
    )

    assert score == 5  # fallback
    assert explanation == "No explanation found."


@patch("src.models.llmscoring_rfp.call_openai_with_tracking")
def test_score_proposal_with_no_tools_or_thoughts(mock_call_openai):
    mock_call_openai.return_value = "Score: 6\nExplanation: Basic but sufficient."

    score, explanation = score_proposal_content_with_llm_and_tools(
        proposal="Minimal proposal",
        criterion="Feasibility"
    )

    assert score == 6
    assert explanation == "Basic but sufficient."
