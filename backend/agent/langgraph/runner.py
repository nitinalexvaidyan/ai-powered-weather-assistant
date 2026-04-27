# agent/langgraph/runner.py --> # run_langgraph_agent

from datetime import datetime

from agent.langgraph.graph_builder import build_graph


graph = build_graph()

def run_langgraph_agent(user_input: str):
    try:
        result = graph.invoke(
            {"user_input": user_input},
            config={"recursion_limit": 5}
        )

        return {
            "success": True,
            "response": result.get("final_response"),
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
