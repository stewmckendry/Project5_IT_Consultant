# tool_tests.py
from src.server.react_agent import ReActConsultantAgent, dispatch_tool_action
from src.utils.tools.tool_catalog_RFP import tool_catalog
import pytest
from src.utils.tools.tool_registry import TOOL_FUNCTION_MAP


def test_tool(tool_name, input_text, section_name="Test Section"):
    print(f"\n🧪 Testing: {tool_name}")

    # Set up a dummy agent object with just what the tool needs
    agent = ReActConsultantAgent(
        section_name=section_name,
        section_text=input_text,
        full_proposal_text=input_text  # optional context
    )

    try:
        result = dispatch_tool_action(agent, f'{tool_name}["{input_text}"]')
        print(f"✅ Output:\n{result}")
    except Exception as e:
        print(f"❌ Error testing {tool_name}: {e}")


# 👇 Sample fixture for mock agent (you can customize it)
@pytest.fixture
def mock_agent():
    class MockAgent:
        section_text = "Our agile methodology uses sprint-based delivery with integrated testing."
        full_proposal_text = "The overall proposal explains modular product support, security compliance, and agile planning."
        section_name = "Methodology"
        memory = {}
    return MockAgent()

# 👇 Generic test to make sure each tool runs without crashing
@pytest.mark.parametrize("tool_name", list(TOOL_FUNCTION_MAP.keys()))
def test_tool_runs_without_error(tool_name, mock_agent):
    tool_fn = TOOL_FUNCTION_MAP[tool_name]
    try:
        result = tool_fn(mock_agent)
        assert result is not None
    except Exception as e:
        pytest.fail(f"Tool '{tool_name}' raised an exception: {str(e)}")
