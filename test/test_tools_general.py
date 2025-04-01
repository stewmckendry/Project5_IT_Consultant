import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from src.utils.tools.tools_general import (
    evaluate_writing_clarity,
    detect_boilerplate_or_marketing_fluff
)
from src.server.react_agent import ReActConsultantAgent

@pytest.fixture
def mock_agent():
    return ReActConsultantAgent(
        section_name="test_general",
        section_text="We deliver innovative, world-class digital transformation at scale.", 
        proposal_text="n/a")

def test_check_writing_clarity(monkeypatch, mock_agent):
    called = {"hit": False}
    def fake_llm(messages, **kwargs):
        called["hit"] = True
        return "The writing is moderately clear and direct."
    monkeypatch.setattr("src.utils.tools.tools_general.call_openai_with_tracking", fake_llm)
    result = evaluate_writing_clarity(mock_agent)
    assert "clear" in result.lower()
    assert called["hit"] is True

def test_detect_boilerplate_or_marketing_fluff(monkeypatch, mock_agent):
    called = {"hit": False}
    def fake_llm(messages, **kwargs):
        called["hit"] = True
        return "This section includes vague, marketing-heavy language such as 'innovative' and 'world-class'."
    
    monkeypatch.setattr("src.utils.tools.tools_general.call_openai_with_tracking", fake_llm)
    result = detect_boilerplate_or_marketing_fluff(mock_agent)
    
    assert any(kw in result.lower() for kw in ["boilerplate", "vague", "marketing", "promotional"])
    assert called["hit"] is True

