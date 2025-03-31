def extract_evaluation_criteria(text: str) -> list:
    """
    Attempts to extract a list of evaluation criteria from a block of RFP text.
    Looks for patterns like:
    - 1. Solution Fit (25%)
    - 2. Vendor Experience - 20%
    - Team – 15%
    Returns list of dicts with name, weight (if found), and any description.
    """
    lines = text.split("\n")
    criteria = []

    for line in lines:
        line = line.strip()
        match = re.match(r"^\d*\.?\s*([A-Za-z\s/&\-]+)[\s\-–:]*(\(?\d{1,3}%?\)?)?", line)
        if match:
            name = match.group(1).strip()
            weight_raw = match.group(2)
            weight = None
            if weight_raw:
                digits = re.findall(r"\d+", weight_raw)
                weight = int(digits[0]) if digits else None
            criteria.append({
                "name": name,
                "weight": weight,
                "description": "",  # Placeholder, will update later
            })

    return criteria


