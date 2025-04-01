import pytest
from pathlib import Path
from src.utils.file_loader import load_scenario_data


def test_load_scenario_data(tmp_path, monkeypatch):
    # Arrange
    base_path = tmp_path / "scenarios"
    scenario_dir = base_path / "basic_scenario"
    scenario_dir.mkdir(parents=True)
    # Create mock RFP and vendor proposal files
    (scenario_dir / "rfp.txt").write_text("## Evaluation Criteria\n1. Solution Fit\n2. Cost")
    (scenario_dir / "vendor_a.txt").write_text("Affordable and simple.")
    (scenario_dir / "vendor_b.txt").write_text("Premium integration features.")

    # Monkeypatch internal path if load_scenario_data is hardcoded
    monkeypatch.chdir(tmp_path.parent)
    
    # Act
    proposals, rfp_file = load_scenario_data("basic_scenario", base_path=base_path)

    # Assert
    assert "Vendor A" in proposals
    assert "Vendor B" in proposals
    assert proposals["Vendor A"].startswith("Affordable")
    assert Path(rfp_file).name == "rfp.txt"
