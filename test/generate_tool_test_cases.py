def generate_unit_test_cases(tool_catalog, num_examples=1):
    """
    Generates a list of (tool_name, input_text) pairs for testing purposes.
    """
    test_cases = []
    for tool_name, meta in tool_catalog.items():
        examples = meta.get("examples", [])
        if examples:
            for ex in examples[:num_examples]:
                match = re.match(rf'{tool_name}\[\"(.+?)\"\]', ex)
                if match:
                    input_text = match.group(1)
                    test_cases.append((tool_name, input_text))
    return test_cases
