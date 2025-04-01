import pytest
from unittest.mock import patch, MagicMock
from src.server.multi_agent_rfpevalrunner import run_multi_proposal_evaluation
from pathlib import Path
import os

@pytest.fixture
def mock_proposals():
    return {
        "Vendor A": "Proposal content A",
        "Vendor B": "Proposal content B"
    }

@patch("src.server.multi_agent_rfpevalrunner.save_markdown_and_pdf")
@patch("src.server.multi_agent_rfpevalrunner.generate_final_comparison_summary")
@patch("src.server.multi_agent_rfpevalrunner.export_proposal_report")
@patch("src.server.multi_agent_rfpevalrunner.evaluate_proposal")
@patch("src.server.multi_agent_rfpevalrunner.Path.mkdir")  # Prevent real dir creation
def test_run_multi_proposal_evaluation_basic(
    mock_mkdir,
    mock_evaluate_proposal,
    mock_export_report,
    mock_generate_summary,
    mock_save_md_pdf,
    mock_proposals
):
    # Setup: Mock the inner functions
    mock_evaluate_proposal.side_effect = [
        ({"score_details": [1, 2]}, 7.5, "SWOT summary A"),
        ({"score_details": [2, 3]}, 8.0, "SWOT summary B"),
    ]
    mock_generate_summary.return_value = ("## Final Summary", "| Vendor | Score |")
    
    # Run the orchestration
    results, summary = run_multi_proposal_evaluation(
        proposals=mock_proposals,
        rfp_criteria=["Solution Fit", "Scalability"],
        model="gpt-3.5-turbo"
    )

    # Assert shape of results
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["vendor_name"] == "Vendor A"
    assert results[1]["vendor_name"] == "Vendor B"
    assert summary.startswith("## Final Summary")

    # Assert that subfunctions were called correctly
    assert mock_evaluate_proposal.call_count == 2
    assert mock_export_report.call_count == 2
    mock_generate_summary.assert_called_once()
    mock_save_md_pdf.assert_called_once()


@patch("src.server.multi_agent_rfpevalrunner.evaluate_proposal")
@patch("src.models.openai_interface.call_openai_with_tracking")
def test_run_multi_proposal_evaluation_with_files(mock_llm, mock_evaluate_proposal, tmp_path):
    # Mock OpenAI response globally (e.g., for summary generation)
    mock_llm.return_value = "Score: 7\nExplanation: Covers all required features. Summary, Cost."

    mock_evaluate_proposal.side_effect = [
    (
        [  # ← this must be a list of dicts, one per criterion
            {
                "criterion": "Solution Fit",
                "proposal_score": 8,
                "top_thoughts": ["Matches system architecture"],
                "all_thoughts": ["Matches system architecture", "Addresses modular design"],
                "triggered_tools": [{"tool": "scalability_checker", "result": "Passed"}],
                "proposal_explanation": "Fits most use cases well."
            }
        ],
        7.8,
        "SWOT summary A: Solution Fit, Cost Effectiveness"
    ),
    (
        [
            {
                "criterion": "Solution Fit",
                "proposal_score": 6,
                "top_thoughts": ["Good but lacking specifics"],
                "all_thoughts": ["Good but lacking specifics", "No mention of scale"],
                "triggered_tools": [{"tool": "compatibility_tool", "result": "Partial match"}],
                "proposal_explanation": "Integration details are vague."
            }
        ],
        6.5,
        "SWOT summary B"
    ),
]


    # Setup temp file structure
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Sample RFP file
    rfp_path = data_dir / "sample_rfp.txt"
    rfp_path.write_text("Evaluation Criteria:\n1. Solution Fit\n2. Cost Effectiveness")

    # Sample proposals (simulate vendor uploads or text inputs)
    proposals = {
        "Vendor A": "We offer a scalable, modular solution at a competitive price.",
        "Vendor B": "Our product integrates easily with your workflow and includes full support."
    }

    # Create outputs dir to verify later
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()

    # Patch the output dir logic inside the function
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)  # Trick to make Path.cwd().parent resolve to tmp_path

        results, summary = run_multi_proposal_evaluation(
            proposals=proposals,
            rfp_file=str(rfp_path),
            model="gpt-3.5-turbo"
        )

        # --- Assertions ---
        # 1. Should have evaluated both vendors
        assert len(results) == 2
        assert any("Solution Fit" in str(summary) or "Cost" in str(summary) for _ in [0])

        # 2. Check if reports were saved in expected path
        #output_report_dir = outputs_dir / "proposal_eval_reports"
        #assert output_report_dir.exists()
        #saved_files = list(output_report_dir.glob("**/*"))
        #assert len(saved_files) > 0  # At least some markdown or PDFs

    finally:
        os.chdir(original_cwd)  # Restore working dir