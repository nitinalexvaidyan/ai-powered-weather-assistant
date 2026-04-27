# agent/langgraph/nodes.py -->  # llm_node, tool_node, respond_node

from services.llm_service import agent_decision
from agent.tools import execute_tool

def llm_node(state):
    user_input = state["user_input"]
    tool_result = state.get("tool_result", "")

    if tool_result:
        context = f"""
            User: {user_input}
            Tool Result: {tool_result}
        """
    else:
        context = f"User: {user_input}"

    decision = agent_decision(context)
    return {"decision": decision}


def tool_node(state):
    decision = state["decision"]
    result = execute_tool(decision, state["user_input"])
    return {"tool_result": str(result)}


def respond_node(state):
    message = state["decision"].get("message", "")
    return {"final_response": message}