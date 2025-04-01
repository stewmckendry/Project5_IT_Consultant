from src.utils.rfp_extractors import extract_evaluation_criteria

def test_extract_simple_criteria_with_percent():
    text = """
    1. Solution Fit (25%)
    2. Vendor Experience (20%)
    3. Team (15%)
    4. Cost (40%)
    """
    result = extract_evaluation_criteria(text)
    assert len(result) == 4
    assert result[0]["name"] == "Solution Fit"
    assert result[0]["weight"] == 25
    assert result[1]["name"] == "Vendor Experience"
    assert result[1]["weight"] == 20

def test_extract_criteria_with_dashes_and_colons():
    text = """
    1. Solution Fit - 25%
    2. Vendor Experience: 20%
    Team – 15%
    Cost – 40%
    """
    result = extract_evaluation_criteria(text)
    names = [c["name"] for c in result]
    weights = [c["weight"] for c in result]
    assert "Solution Fit" in names
    assert "Vendor Experience" in names
    assert "Team" in names
    assert weights == [25, 20, 15, 40]

def test_extract_without_weights():
    text = """
    1. Solution Fit
    2. Team
    3. Cost
    """
    result = extract_evaluation_criteria(text)
    assert all(c["weight"] is None for c in result)
    assert result[0]["name"] == "Solution Fit"
    assert result[2]["name"] == "Cost"

def test_extract_ignores_non_criteria_lines():
    text = """
    Evaluation Criteria

    1. Solution Fit (25%)
    Some explanation here that should be ignored.
    2. Team (15%)
    """
    result = extract_evaluation_criteria(text)
    assert len(result) == 2
    assert result[0]["name"] == "Solution Fit"
    assert result[1]["name"] == "Team"
    assert result[0]["weight"] == 25