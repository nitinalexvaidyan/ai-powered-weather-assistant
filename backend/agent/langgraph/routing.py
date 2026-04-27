# agent/langgraph/routing.py -->  # route_decision

def route_decision(state):
    action = state["decision"].get("action")

    if action == "call_tool":
        return "tool"

    return "respond"