TOOL_REGISTRY = {}


def register_tool(name):
    def decorator(func):
        TOOL_REGISTRY[name] = func
        return func
    return decorator


def execute_tool(tool_name, args, user_input):
    tool = TOOL_REGISTRY.get(tool_name)

    if not tool:
        return f"Error: Unknown tool '{tool_name}'"

    try:
        return tool(args, user_input)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"