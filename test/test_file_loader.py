import pytest
from src.utils.file_loader import (
    load_report_text_from_file,
    load_proposals_from_folder,
    load_rfp_criteria,
    parse_rfp_from_file,
    preprocess_proposal_for_criteria_with_threshold
)
from pathlib import Path

# --------- Mocks + Fixtures ---------
@pytest.fixture
def sample_txt_file(tmp_path):
    content = "Background\nThis is a sample.\nEvaluation Criteria\n1. Solution Fit\n2. Team\n"
    file = tmp_path / "sample.txt"
    file.write_text(content)
    return str(file)

@pytest.fixture
def sample_proposal_folder(tmp_path):
    file = tmp_path / "VendorA.txt"
    file.write_text("Our solution is modular and scalable.\nIt supports real-time scheduling.")
    return tmp_path

# --------- Test Cases ---------
def test_load_report_text_from_file(sample_txt_file):
    text = load_report_text_from_file(sample_txt_file)
    assert "Evaluation Criteria" in text

def test_load_proposals_from_folder(sample_proposal_folder):
    proposals = load_proposals_from_folder(sample_proposal_folder)
    assert "VendorA" in proposals
    assert "modular" in proposals["VendorA"]

def test_parse_rfp_from_file(sample_txt_file):
    parsed = parse_rfp_from_file(sample_txt_file)
    assert "Evaluation Criteria" in parsed["sections"]
    names = [c["name"] for c in parsed["criteria"]]
    assert "Team" in names

def test_preprocess_proposal_for_criteria_with_threshold():
    proposal = "Our solution is scalable.\nIt meets privacy and accessibility standards."
    rfp_criteria = ["Solution Fit", "Privacy & Accessibility"]
    results = preprocess_proposal_for_criteria_with_threshold(proposal, rfp_criteria)
    assert all(k in results for k in rfp_criteria)

def test_preprocess_returns_expected_matches():
    proposal_text = (
        "Our solution includes a scalable EHR platform.\n"
        "The team has experience working with public health systems.\n"
        "Pricing is based on a subscription model."
    )

    criteria = ["Solution Fit", "Team", "Cost"]

    result = preprocess_proposal_for_criteria_with_threshold(proposal_text, criteria)

    assert "scalable EHR" in result["Solution Fit"]
    assert "experience working with public health" in result["Team"]
    assert "subscription model" in result["Cost"]

def test_preprocess_respects_threshold():
    text = (
        "Our solution uses APIs.\n"
        "We support agile delivery.\n"
        "Security is built-in at every layer."
    )
    criteria = ["Security", "APIs"]

    result_low = preprocess_proposal_for_criteria_with_threshold(text, criteria, score_threshold=0.1)
    result_high = preprocess_proposal_for_criteria_with_threshold(text, criteria, score_threshold=0.9)

    # At low threshold, more matches should appear
    assert len(result_low["Security"]) >= len(result_high["Security"])


def test_preprocess_fallback_to_top_match_if_none_above_threshold():
    text = (
        "Completely unrelated paragraph.\n"
        "Another vague line.\n"
        "Still nothing relevant."
    )
    criteria = ["Quantum Computing"]

    result = preprocess_proposal_for_criteria_with_threshold(text, criteria, score_threshold=0.99)

    # Should return at least one fallback paragraph
    assert result["Quantum Computing"] != ""
    assert isinstance(result["Quantum Computing"], str)

