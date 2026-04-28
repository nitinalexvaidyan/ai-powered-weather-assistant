from agents.base_agent import BaseAgent
from agents.aqi.tools import get_aqi_tool
from graph.runner import run_langgraph_agent

class AQIAgent(BaseAgent):
    def __init__(self):
        super().__init__("aqi")


    def run(self, query, session_id):
        tools = {
            "get_air_quality": get_aqi_tool
        }

        return run_langgraph_agent(query, session_id, tools)