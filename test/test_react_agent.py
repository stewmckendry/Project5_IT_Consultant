# test/test_react_agent.py

import pytest
from src.server.react_agent import ReActConsultantAgent


@pytest.fixture
def sample_agent():
    return ReActConsultantAgent(
        section_name="Implementation Plan",
        section_text="This section describes our phased rollout strategy...",
        proposal_text="Full proposal text goes here...",
    )


def test_agent_initialization(sample_agent):
    assert sample_agent.section_name == "Implementation Plan"
    assert "phased rollout" in sample_agent.section_text
    assert "Full proposal" in sample_agent.full_proposal_text


def test_build_react_prompt_forRFPeval_contains_expected_text(sample_agent):
    prompt_messages = sample_agent.build_react_prompt_forRFPeval(
        criterion=sample_agent.section_name,
        section_text=sample_agent.section_text,
        full_proposal_text=sample_agent.full_proposal_text
    )
    
    assert isinstance(prompt_messages, list)
    assert any("Implementation Plan" in msg["content"] for msg in prompt_messages)
    assert any("phased rollout strategy" in msg["content"] for msg in prompt_messages)
