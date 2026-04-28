TOOL_REGISTRY = {}


def register_tool(name, description, args_schema):
    def decorator(func):
        TOOL_REGISTRY[name] = {
            "func": func,
            "description": description,
            "args": args_schema
        }
        return func
    return decorator


def execute_tool(tool_name, args, user_input):
    tool_entry = TOOL_REGISTRY.get(tool_name)

    if not tool_entry:
        return f"Error: Unknown tool '{tool_name}'"

    try:
        return tool_entry["func"](args, user_input)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"