from src.server.react_agent import parse_thought_action
import pytest

def test_parse_thought_action_basic():
    response = "Thought: Clear alignment with goals.\nAction: evaluate_solution_fit"
    thought, action = parse_thought_action(response)
    assert thought == "Clear alignment with goals."
    assert action == "evaluate_solution_fit"

def test_parse_thought_action_whitespace_and_case():
    response = "  thought: Matches use case.\n  Action: suggest_tool"
    thought, action = parse_thought_action(response)
    assert thought == "Matches use case."
    assert action == "suggest_tool"

def test_parse_thought_action_missing_parts():
    with pytest.raises(ValueError):
        parse_thought_action("No thought or action here")
