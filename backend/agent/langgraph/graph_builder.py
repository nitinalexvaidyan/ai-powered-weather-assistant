# agent/langgraph/graph_builder.py --> # graph construction

from langgraph.graph import StateGraph
from agent.langgraph.state import AgentState
from agent.langgraph.nodes import llm_node, tool_node, respond_node
from agent.langgraph.routing import route_decision


def build_graph():

    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("llm", llm_node)
    builder.add_node("tool", tool_node)
    builder.add_node("respond", respond_node)

    # Entry
    builder.set_entry_point("llm")

    # Conditional routing
    builder.add_conditional_edges(
        "llm",
        route_decision,
        {
            "tool": "tool",
            "respond": "respond"
        }
    )

    # Loop
    builder.add_edge("tool", "llm")

    # End
    builder.set_finish_point("respond")

    return builder.compile()