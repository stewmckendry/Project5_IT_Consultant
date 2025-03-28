# visualization.py – Tool usage display

from utils.tools.tools_reasoning import categorize_tools_by_priority
from utils.tools.tool_catalog import tool_priority_map, global_tools
import matplotlib.pyplot as plt


def print_tool_usage(agent):
    """
    Prints the usage of tools categorized by their priority.

    Purpose:
    This function categorizes the usage of tools into four categories: Primary, Optional, Global, and Uncategorized. It then prints the usage count of each tool within these categories.

    Parameters:
    agent (ReActConsultantAgent): An instance of the ReActConsultantAgent class, which contains the tool usage data to be categorized and printed.

    Workflow:
    1. Calls the categorize_tools_by_priority function to categorize the tools based on their priority.
    2. Iterates through each category (Primary, Optional, Global, Uncategorized).
    3. For each category, retrieves the tools and their usage counts.
    4. Prints the category name and the usage count of each tool within the category, sorted by usage count in descending order.

    Returns:
    None
    """
    print("\n📊 Tool Usage by Category:")

    categorized = categorize_tools_by_priority(
        agent.tool_usage, 
        tool_priority_map, 
        global_tools
    )

    for category in ["Primary", "Optional", "Global", "Uncategorized"]:
        tools = categorized[category]
        if tools:
            print(f"\n🔹 {category} Tools:")
            for tool, count in sorted(tools.items(), key=lambda x: -x[1]):
                print(f"  - {tool}: {count} times")


def plot_tool_usage(tool_usage_dict, title="Tool Usage Summary"):
    """
    Plots the usage of tools categorized by their priority.

    Purpose:
    This function visualizes the usage of tools in a horizontal bar chart, categorized by their priority (Primary, Optional, Global, Uncategorized). It helps in understanding the distribution of tool usage based on their priority and scope.

    Parameters:
    tool_usage_dict (dict): A dictionary where keys are tool names and values are their respective usage counts.
    title (str): The title of the plot. Default is "Tool Usage Summary".

    Workflow:
    1. Calls the categorize_tools_by_priority function to categorize the tools based on their priority.
    2. Initializes lists to store tool names, usage counts, and colors for plotting.
    3. Iterates through each category (Primary, Optional, Global, Uncategorized) and appends the tool names, counts, and corresponding colors to the lists.
    4. Creates a horizontal bar plot using matplotlib with the tool names, counts, and colors.
    5. Adds usage count labels to each bar.
    6. Inverts the y-axis to display the highest usage count at the top.
    7. Adds a legend to the plot indicating the tool categories.
    8. Displays the plot.

    Returns:
    None
    """
    categorized = categorize_tools_by_priority(
        tool_usage_dict, 
        tool_priority_map, 
        global_tools
    )

    # Combine for plotting
    tools, counts, colors = [], [], []
    color_map = {"Primary": "green", "Optional": "orange", "Global": "blue", "Uncategorized": "gray"}

    for category in ["Primary", "Optional", "Global", "Uncategorized"]:
        for tool, count in categorized[category].items():
            tools.append(tool)
            counts.append(count)
            colors.append(color_map[category])

    plt.figure(figsize=(10, 6))
    bars = plt.barh(tools, counts, color=colors)
    plt.xlabel("Usage Count")
    plt.title(title)

    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.2, bar.get_y() + bar.get_height()/2, str(int(width)), va='center')

    plt.gca().invert_yaxis()
    plt.tight_layout()

    # Add legend
    legend_patches = [mpatches.Patch(color=color_map[c], label=c) for c in color_map]
    plt.legend(handles=legend_patches, title="Tool Category", loc="lower right")

    plt.show()

