import pytest
from unittest.mock import patch, MagicMock
from src.server.react_agent import run_react_loop_for_rfp_eval


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    agent.model = "gpt-4"
    agent.temperature = 0.3
    agent.history = []
    agent.build_react_prompt_forRFPeval.return_value = [{"role": "user", "content": "mocked prompt"}]
    return agent


@patch("src.server.react_agent.call_openai_with_tracking")
@patch("src.server.react_agent.dispatch_tool_action")
def test_run_react_loop_basic(mock_dispatch_tool_action, mock_call_openai, mock_agent):
    mock_call_openai.return_value = (
        "thought: This proposal seems strong on adaptability. \n"
        "action: evaluate_solution_fit\n"
    )
    mock_dispatch_tool_action.return_value = "✔️ Tool result: Adaptable across units"

    result = run_react_loop_for_rfp_eval(
        agent=mock_agent,
        criterion="Solution Fit",
        section_text="The vendor claims their product supports multiple teams.",
        full_proposal_text="Full vendor proposal text here.",
        max_steps=1
    )

    assert len(result) == 1
    step = result[0]
    assert step["action"] == "evaluate_solution_fit"
    assert "thought" in step
    assert "observation" in step


@patch("src.server.react_agent.call_openai_with_tracking")
@patch("src.server.react_agent.dispatch_tool_action")
def test_react_loop_stops_on_summarize(mock_dispatch, mock_call_openai, mock_agent):
    mock_call_openai.return_value = "Thought: We're done.\nAction: summarize"
    mock_dispatch.return_value = "Summary complete."

    result = run_react_loop_for_rfp_eval(
        agent=mock_agent,
        criterion="Benefits",
        section_text="some summary",
        full_proposal_text="...",
        max_steps=4
    )

    assert len(result) == 1
    assert result[0]["action"] == "summarize"
    mock_dispatch.assert_called_once()


@patch("src.server.react_agent.call_openai_with_tracking")
@patch("src.server.react_agent.dispatch_tool_action")
def test_react_loop_handles_parsing_errors(mock_dispatch, mock_call_openai, mock_agent):
    mock_call_openai.return_value = "INVALID LLM RESPONSE"

    result = run_react_loop_for_rfp_eval(
        agent=mock_agent,
        criterion="Security",
        section_text="secure section",
        full_proposal_text="...",
        max_steps=2
    )

    assert result == []
    assert len(mock_agent.history) == 0
    mock_dispatch.assert_not_called()


