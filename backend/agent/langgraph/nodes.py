# agent/langgraph/nodes.py -->  # llm_node, tool_node, respond_node

from services.llm_service import agent_decision
from agent.tools.registry import execute_tool

def llm_node(state):
    messages = state.get("messages", [])[-6:]
    trace = state.get("trace", []).copy()
    context = "\n".join(messages)
    decision = agent_decision(context)

    # 🔥 Add trace
    trace.append({
        "step": len(trace) + 1,
        "action": decision.get("action"),
        "tool": decision.get("tool_name")
    })

    return {
        "decision": decision,
        "trace": trace
    }



def tool_node(state):
    decision = state["decision"]
    trace = state.get("trace", []).copy()

    tool_name = decision.get("tool_name")
    args = decision.get("arguments", {})

    result = execute_tool(tool_name, args, state["user_input"])

    if trace:
        trace[-1]["tool_result"] = str(result)[:200]

    messages = state.get("messages", []).copy()
    messages.append(f"{tool_name} result: {result}")

    return {
        "tool_result": str(result),
        "messages": messages,
        "trace": trace
    }

def respond_node(state):
    decision = state["decision"]
    trace = state.get("trace", []).copy()
    message = decision.get("message", "")

    # 🔥 Update trace
    if trace:
        trace[-1]["message"] = message

    messages = state.get("messages", []).copy()
    messages.append(f"Assistant: {message}")

    return {
        "final_response": message,
        "messages": messages,
        "trace": trace
    }