# tools_reasoning.py – Reasoning, math, and selection tools

# Tool picker: Pick tools based on intent description
# This function picks tools from the tool catalog based on the intent description.
# It searches through the tool catalog and returns a list of tools whose descriptions match the given intent description.

def pick_tool_by_intent(intent_description, tool_catalog):
    """
    Picks tools from the tool catalog based on the intent description.

    Purpose:
    This function searches through the tool catalog and returns a list of tools whose descriptions match the given intent description.

    Parameters:
    intent_description (str): A description of the intent to match against tool descriptions.
    tool_catalog (dict): A dictionary where keys are tool names and values are dictionaries containing tool metadata, including 'description'.

    Workflow:
    1. Initializes an empty list `matches` to store the names of matching tools.
    2. Iterates through each tool in the `tool_catalog` dictionary.
    3. For each tool, checks if the `intent_description` is present in the tool's description (case-insensitive).
    4. If a match is found, appends the tool name to the `matches` list.
    5. Returns the list of matching tools.

    Returns:
    list: A list of tool names whose descriptions match the given intent description.
    """
    matches = []
    for tool, meta in tool_catalog.items():
        if intent_description.lower() in meta["description"].lower():
            matches.append(tool)
    return matches


# Tool picker: Pick tools based on fuzzy intent description matching
# This function picks tools from the tool catalog based on a fuzzy intent description matching.
# It uses fuzzy string matching to find tools whose descriptions closely match the given intent description.

def pick_tool_by_intent_fuzzy(intent_description, tool_catalog, threshold=0.3):
    """
    Picks tools from the tool catalog based on a fuzzy intent description matching.

    Purpose:
    This function uses fuzzy string matching to find tools whose descriptions closely match the given intent description.

    Parameters:
    intent_description (str): A description of the intent to match against tool descriptions.
    tool_catalog (dict): A dictionary where keys are tool names and values are dictionaries containing tool metadata, including 'description'.
    threshold (float): The minimum similarity ratio (between 0 and 1) to consider a match. Default is 0.3.

    Workflow:
    1. Initializes an empty list `matches` to store the names and similarity ratios of matching tools.
    2. Iterates through each tool in the `tool_catalog` dictionary.
    3. For each tool, calculates the similarity ratio between the `intent_description` and the tool's description using `SequenceMatcher`.
    4. If the similarity ratio exceeds the `threshold`, appends the tool name and ratio to the `matches` list.
    5. Sorts the `matches` list by similarity ratio in descending order.

    Returns:
    list: A list of tuples, where each tuple contains a tool name and its similarity ratio, sorted by best match.
    """
    matches = []
    for tool, meta in tool_catalog.items():
        ratio = SequenceMatcher(None, intent_description.lower(), meta["description"].lower()).ratio()
        if ratio > threshold:
            matches.append((tool, round(ratio, 2)))
    return sorted(matches, key=lambda x: -x[1])  # sort by best match


def categorize_tools_by_priority(tool_usage, section_tool_map, global_tools):
    """
    Categorizes each tool usage as Global, Primary, or Optional.

    Purpose:
    This function categorizes the usage of tools into four categories: Global, Primary, Optional, and Uncategorized. It helps in understanding the distribution of tool usage based on their priority and scope.

    Parameters:
    tool_usage (dict): A dictionary where keys are tool names and values are their respective usage counts.
    section_tool_map (dict): A dictionary where keys are section names and values are dictionaries containing 'primary' and 'optional' tools for each section.
    global_tools (list): A list of tools that are considered global and can be used across any section.

    Workflow:
    1. Initializes a dictionary `categorized` with keys 'Global', 'Primary', 'Optional', and 'Uncategorized', each containing an empty dictionary.
    2. Iterates through each tool and its count in the `tool_usage` dictionary.
    3. Checks if the tool is in the `global_tools` list. If yes, adds it to the 'Global' category and marks it as matched.
    4. Iterates through the `section_tool_map` to check if the tool is listed as 'primary' or 'optional' for any section. If found, adds it to the respective category and marks it as matched.
    5. If the tool is not matched in any category, adds it to the 'Uncategorized' category.
    6. Returns the `categorized` dictionary containing the categorized tool usage.

    Returns:
    dict: A dictionary where keys are categories ('Global', 'Primary', 'Optional', 'Uncategorized') and values are dictionaries of tools and their usage counts.
    """
    categorized = {"Global": {}, "Primary": {}, "Optional": {}, "Uncategorized": {}}

    for tool, count in tool_usage.items():
        matched = False
        # Check if tool is in global
        if tool in global_tools:
            categorized["Global"][tool] = count
            matched = True
        # Check if tool is in primary/optional across any section
        for priorities in section_tool_map.values():
            if tool in priorities.get("primary", []):
                categorized["Primary"][tool] = count
                matched = True
            elif tool in priorities.get("optional", []):
                categorized["Optional"][tool] = count
                matched = True
        if not matched:
            categorized["Uncategorized"][tool] = count

    return categorized


def analyze_math_question(expression):
    """
    Analyzes and evaluates a mathematical expression using the LLMMathChain.

    Purpose:
    This function takes a mathematical expression as input, evaluates it using the LLMMathChain, 
    and returns the result. It handles any exceptions that may occur during the evaluation process.

    Parameters:
    expression (str): The mathematical expression to be evaluated.

    Workflow:
    1. Receives a mathematical expression as input.
    2. Calls the `run` method of the `llm_math` object to evaluate the expression.
    3. If the evaluation is successful, returns the result.
    4. If an exception occurs during the evaluation, catches the exception and returns an error message.

    Returns:
    str: The result of the evaluated mathematical expression, or an error message if the evaluation fails.
    """
    try:
        result = llm_math.invoke(expression)
        return result
    except Exception as e:
        return f"⚠️ Math error: {str(e)}"


