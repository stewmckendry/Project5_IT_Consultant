# text_processing.py – Preprocessing, section parsing, normalization

def split_report_into_sections(report_text):
    """
    Splits a report into sections based on headers.

    Purpose:
    This function processes a report text and splits it into sections using headers as delimiters. 
    It identifies headers based on lines ending with a colon (":") and assumes that headers contain 
    up to four words. Content before the first header is treated as the "Introduction" section.

    Parameters:
    report_text (str): The full text of the report to be split into sections.

    Workflow:
    1. Initializes an empty dictionary `sections` to store the output as {section_name: text}.
    2. Splits the report into lines and iterates through each line.
    3. Skips blank lines.
    4. Detects section headers based on lines ending with a colon and containing up to four words.
       - If a header is detected:
         a. Saves the content of the previous section (if any) into the `sections` dictionary.
         b. Updates the `current_section` to the new header.
         c. Clears the buffer for the new section's content.
       - If no header is detected, appends the line to the buffer for the current section.
    5. After processing all lines, saves the content of the last section or treats it as "Introduction" 
       if no headers were found.
    6. Returns the `sections` dictionary containing section names as keys and their corresponding content as values.

    Returns:
    dict: A dictionary where keys are section names and values are the corresponding section content.
    """
    sections = {}       # To store final output as {section_name: text}
    lines = report_text.strip().split("\n")  # Break the report into lines
    current_section = None  # Track the active section label
    buffer = []        # Temporarily hold lines belonging to the current section

    for line in lines:
        line = line.strip()
        if not line:
            continue  # skip blank lines

        # Detect section header
        if line.endswith(":") and len(line.split()) <= 4:
            # Store previous buffer if it exists
            if current_section is None and buffer:  # Handle content before the first header
                sections["Introduction"] = "\n".join(buffer).strip()
            elif current_section:  # Save the previous section's content
                sections[current_section] = "\n".join(buffer).strip()

            current_section = line.replace(":", "").strip()  # Update the current_section label
            buffer = []  # Clear the buffer for new section content
        else:
            buffer.append(line)  # Add line to buffer for the current section

    # Save last section or intro
    if current_section:  # Save the last section's content
        sections[current_section] = "\n".join(buffer).strip()
    elif buffer:  # Handle content with no headers
        sections["Introduction"] = "\n".join(buffer).strip()

    # After section splitting
    normalized_sections = {}
    for label, text in sections.items():
        canonical = map_section_to_canonical(label)
        normalized_sections[canonical or label] = text  # use original if no match

    return normalized_sections


def map_section_to_canonical(label, threshold=0.6, use_llm_fallback=True):
    """
    Maps a section label to its canonical name.

    Purpose:
    This function attempts to map a given section label to a canonical section name using a combination of direct matching, fuzzy matching, and optionally a language model fallback. It is useful for normalizing section names in a report to a standard set of canonical names.

    Parameters:
    label (str): The section label to map to a canonical name.
    threshold (float): The similarity threshold for fuzzy matching. Default is 0.6.
    use_llm_fallback (bool): Whether to use a language model fallback if no match is found. Default is True.

    Workflow:
    1. Cleans the input label by stripping whitespace and converting it to lowercase.
    2. Performs direct matching:
       - Checks if the label matches any canonical name or its variants directly or as a substring.
    3. Performs fuzzy matching:
       - Uses fuzzy string matching to find the closest match among all canonical names and their variants.
       - If a match is found with a similarity ratio above the threshold, returns the corresponding canonical name.
    4. Uses a language model fallback (optional):
       - If no match is found through direct or fuzzy matching, calls the `guess_canonical_section_with_llm` function to infer the canonical name using a language model.
    5. Returns `None` if no match is found through any method.

    Returns:
    str or None: The canonical section name if a match is found, or `None` if no match is found.
    """
    label_clean = label.strip().lower()

    # 1. Direct and substring match
    for canonical, variants in canonical_section_map.items():
        for variant in variants:
            if variant in label_clean:
                return canonical
        if canonical.lower() in label_clean:
            return canonical

    # 2. Fuzzy match
    all_variants = {v.lower(): canon for canon, variants in canonical_section_map.items() for v in variants}
    match = difflib.get_close_matches(label_clean, all_variants.keys(), n=1, cutoff=threshold)
    if match:
        return all_variants[match[0]]

    # 3. LLM fallback
    if use_llm_fallback:
        return guess_canonical_section_with_llm(label)

    return None


def guess_canonical_section_with_llm(label, model="gpt-3.5-turbo", temperature=0.2):
    """
    Uses LLM to guess the canonical section name from a list of known options.

    Returns:
    str or None
    """
    canonical_names = list(canonical_section_map.keys())
    prompt = (
        "You're an expert in business consulting. "
        "Given this section title: '{label}', what is the most likely standard section label "
        "from the following options:\n\n"
        + ", ".join(canonical_names) +
        "\n\nReturn only the best matching label. If unsure, return 'Unknown'."
    ).replace("{label}", label.strip())

    messages = [{"role": "user", "content": prompt}]
    result = call_openai_with_tracking(messages, model=model, temperature=temperature)

    cleaned = result.strip()
    if cleaned in canonical_names:
        return cleaned
    elif "unknown" in cleaned.lower():
        return None
    else:
        # Try fuzzy match if response is slightly off (e.g., "Implementation Timeline")
        return difflib.get_close_matches(cleaned, canonical_names, n=1, cutoff=0.6)[0] if difflib.get_close_matches(cleaned, canonical_names) else None
    

# Define the canonical section map for mapping section names to canonical names (similar to the tool catalog)
canonical_section_map = {
    "Introduction": ["header", "intro", "project context", "introduction", "overview"],
    "Summary": ["summary", "executive summary"],
    "Goals & Objectives": ["goals", "objectives", "strategic priorities"],
    "Current State Assessment": ["current state", "as-is", "status quo"],
    "Future State": ["future state", "to-be", "vision", "target state"],
    "Key Recommendations": ["recommendations", "our recommendations", "next steps"],
    "Implementation Plan": ["implementation plan", "roadmap", "deployment", "schedule", "timeline", "phasing"],
    "Benefits": ["benefits", "value", "expected outcomes"],
    "Costs": ["costs", "financials", "budget", "investment"],
    "Resources": ["resources", "team structure", "staffing", "governance"],
    "Risks & Mitigations": ["risks", "mitigations", "risk mitigation"]
}

