import pytest
from src.server.proposal_eval import evaluate_proposal
from unittest.mock import patch

class DummyAgent:
    def __init__(self):
        self.memory = {}
        self.section_name = ""
        self.section_text = ""
        self.proposal_text = ""

    def build_react_prompt_forRFPeval(self, criterion, section_text, full_proposal_text):
        return [{"role": "user", "content": f"Prompt for {criterion}"}]

    def run_react_loop_check_withTool(self, prompt, criterion=None):
        return f"Mock result for {criterion or 'unknown'}"

# 🔧 This patch will stub ALL OpenAI calls during the test
@patch("src.models.openai_interface.call_openai_with_tracking")
def test_evaluate_proposal_stores_results(mock_openai):
    # Stub response for any OpenAI call
    mock_openai.return_value = "stubbed openai response ✅"

    # Mock proposal and criteria
    proposal = "This is the full proposal text."
    criteria = ["Solution Fit", "Team", "Cost"]
    agent = DummyAgent()

    # Run the function
    result, overall_score, swot = evaluate_proposal(proposal, criteria, agent)

    # Check structure
    assert isinstance(result, list)
    assert isinstance(overall_score, float)
    assert isinstance(swot, str)

    # Check that we got all criteria back
    result_criteria = [r["criterion"] for r in result]
    for c in criteria:
        assert c in result_criteria