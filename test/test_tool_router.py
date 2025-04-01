# test/test_tool_router.py

import pytest
from src.server.react_agent import dispatch_tool_action, ReActConsultantAgent
from src.utils.tools.tool_dispatch import TOOL_FUNCTION_MAP

# ---- Mock setup ----

class DummyAgent:
    def __init__(self):
        self.section_text = "This is a test section."
        self.section_name = "Test Section"
        self.full_proposal_text = "Full proposal context here."
        self.memory = {}

# Replace actual tool with mock for test purposes
@pytest.fixture
def mock_tool_fn(monkeypatch):
    def fake_tool_fn(*args, **kwargs):
        return "✅ Tool executed"
    TOOL_FUNCTION_MAP["mock_tool"] = fake_tool_fn
    return fake_tool_fn

@pytest.fixture
def agent():
    return DummyAgent()


# ---- Tests ----

def test_dispatch_known_tool_with_argument(agent):
    def fake_tool_fn(input_text, agent):
        return "✅ Tool executed"
    tool_map = {"mock_tool": fake_tool_fn}
    action = 'mock_tool["evaluate product fit"]'
    result = dispatch_tool_action(agent, action, tool_map=tool_map)
    assert "✅ Tool executed" in result


def test_dispatch_unknown_tool(agent):
    action = 'nonexistent_tool["evaluate security"]'
    result = dispatch_tool_action(agent, action)
    assert "not recognized" in result.lower()

def test_dispatch_malformed_action(agent):
    action = "malformed[no_quote]"
    result = dispatch_tool_action(agent, action)
    assert "could not parse" in result.lower()

def test_dispatch_tool_typeerror(agent):
    def tool_with_wrong_sig():
        return "Should fail"
    tool_map = {"bad_tool": tool_with_wrong_sig}

    action = 'bad_tool["input"]'
    result = dispatch_tool_action(agent, action, tool_map=tool_map)
    assert "Tool execution error" in result
