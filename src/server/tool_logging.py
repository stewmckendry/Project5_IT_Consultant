import inspect

def log_tool_execution(tool_name, tool_fn, input_arg=None, agent=None):
    fn_module = inspect.getmodule(tool_fn).__name__
    input_preview = input_arg[:100] + "..." if input_arg and len(input_arg) > 100 else input_arg
    print(f"🧪 Executing tool: {tool_name} from {fn_module}")
    if input_arg:
        print(f"🔹 Input: {input_preview}")
    if agent and hasattr(agent, 'section_name'):
        print(f"📄 Section: {agent.section_name}")
