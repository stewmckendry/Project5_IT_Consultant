import pytest
from src.utils import logging_utils


def test_log_phase_and_result(caplog):
    caplog.set_level("INFO", logger="ProposalEvaluator")
    logging_utils.log_phase("Begin eval")
    logging_utils.log_result("Vendor Z", "Scalability", 7)

    assert "📌 Begin eval" in caplog.text
    assert "✅ [Vendor Z] 'Scalability' scored 7/10" in caplog.text


def test_log_tool_usage_and_summary(caplog):
    caplog.set_level("DEBUG", logger="ProposalEvaluator")
    logging_utils.tool_stats.clear()

    logging_utils.log_tool_used("test_tool")
    logging_utils.log_tool_used("test_tool")
    logging_utils.log_tool_used("extra_tool")
    logging_utils.print_tool_stats()

    assert "test_tool: 2" in caplog.text
    assert "extra_tool: 1" in caplog.text


def test_log_thought_scores_and_summary(caplog):
    caplog.set_level("DEBUG", logger="ProposalEvaluator")
    logging_utils.thought_stats.clear()

    logging_utils.log_thought_score("Thought A", 0.9)
    logging_utils.log_thought_score("Thought A", 0.8)
    logging_utils.log_thought_score("Thought B", 0.6)
    logging_utils.print_thought_stats()

    assert "Thought A: 2" in caplog.text
    assert "Thought B: 1" in caplog.text


def test_log_openai_calls_and_summary(caplog):
    caplog.set_level("DEBUG", logger="ProposalEvaluator")
    logging_utils.openai_call_counter = 0  # Reset between tests

    logging_utils.log_openai_call("Prompt X", "Response X")
    logging_utils.log_openai_call("Prompt Y", "Response Y")
    logging_utils.print_openai_call_stats()

    assert "🔄 OpenAI call #2" in caplog.text or "Total OpenAI calls made: 2" in caplog.text


def test_log_tool_execution_details(caplog):
    caplog.set_level("INFO", logger="ProposalEvaluator")

    def dummy_tool(x): return x
    logging_utils.log_tool_execution("dummy_tool", dummy_tool, input_arg="some input string")

    assert "Executing tool: dummy_tool" in caplog.text
    assert "Input: some input string" in caplog.text
