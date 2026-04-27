# agent/langgraph/runner.py --> # run_langgraph_agent

from datetime import datetime
from agent.langgraph.graph_builder import build_graph
from agent.langgraph.memory_store import get_session_memory, update_session_memory



graph = build_graph()

def run_langgraph_agent(user_input: str, session_id: str):
    try:
        memory = get_session_memory(session_id)
        messages = memory["messages"]
        trace = memory["trace"]
        result = graph.invoke(
            {
                "user_input": user_input,
                "messages": messages + [f"User: {user_input}"],
                "trace": trace
            },
            config={"recursion_limit": 7}
        )
        
        update_session_memory(
            session_id,
            result.get("messages", []),
            result.get("trace", [])
        )

        return {
            "success": True,
            "response": result.get("final_response"),
            "trace": result.get("trace"),
            "session_id": session_id,
            "error": None,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "response": "Something went wrong, Please try after sometime",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
