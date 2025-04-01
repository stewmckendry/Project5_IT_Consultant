import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from src.utils.tools.tools_RFP_team import (
    check_team_experience_alignment
)
from src.server.react_agent import ReActConsultantAgent

@pytest.fixture
def mock_agent_team():
    return ReActConsultantAgent(section_name="test_team", 
                                section_text="Our senior architect has 20 years in public sector health.", 
                                proposal_text="n/a")

def test_check_team_experience_alignment(monkeypatch, mock_agent_team):
    called = {"hit": False}
    def fake_llm(messages, **kwargs):
        called["hit"] = True
        return "The team experience aligns with the project goals and demonstrates relevant background."
    monkeypatch.setattr("src.utils.tools.tools_RFP_team.call_openai_with_tracking", fake_llm)
    result = check_team_experience_alignment(mock_agent_team)
    assert "aligns" in result.lower()
    assert called["hit"] is True
