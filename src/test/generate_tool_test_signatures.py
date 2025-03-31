from src.utils.tools.tool_registry import TOOL_FUNCTION_MAP
import inspect

def generate_unit_test_sigs():
    lines = []
    for tool_name, fn in TOOL_FUNCTION_MAP.items():
        sig = inspect.signature(fn)
        params = list(sig.parameters.keys())

        test_name = f"test_{tool_name}"
        param_str = ", ".join("mock_" + p for p in params)

        lines.append(f"def {test_name}({param_str}):")
        lines.append(f"    # TODO: Implement test for {tool_name}")
        lines.append(f"    result = {tool_name}({', '.join('mock_' + p for p in params)})")
        lines.append(f"    assert result is not None")
        lines.append("")
    
    fn = "\n".join(lines)
    with open("../test/test_tools_autogen.py", "w") as f:
        f.write(fn)
    print(f"Generated test signatures for all tools in {TOOL_FUNCTION_MAP.keys()} and saved to test/test_tools_autogen.py")

