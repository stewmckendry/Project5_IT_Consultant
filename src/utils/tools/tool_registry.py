import importlib
import inspect
from src.utils.tools import (
    tools_general,
    tools_basic,
    tools_nlp,
    tools_reasoning,
    tools_RFP_team,
    tools_rfp_experience,
    tools_RFP_plan,
    tools_rfp_method,
    tools_RFP_costs,
    tools_RFP_risk,
    tools_RFP_fit
)
from src.utils.tools.tool_catalog_RFP import tool_catalog  # or your merged version

# List of modules to scan
tool_modules = [
    tools_general,
    tools_basic,
    tools_nlp,
    tools_reasoning,
    tools_RFP_team,
    tools_rfp_experience,
    tools_RFP_plan,
    tools_rfp_method,
    tools_RFP_costs,
    tools_RFP_risk,
    tools_RFP_fit
]

def build_tool_function_map():
    tool_function_map = {}
    for tool_name in tool_catalog.keys():
        for module in tool_modules:
            if hasattr(module, tool_name):
                func = getattr(module, tool_name)
                if inspect.isfunction(func):
                    tool_function_map[tool_name] = func
                    break
    return tool_function_map

# Generate it!
TOOL_FUNCTION_MAP = build_tool_function_map()
