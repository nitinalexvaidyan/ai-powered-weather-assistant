from agents.base_agent import BaseAgent
from agents.weather.tools import weather_tool
from graph.runner import run_langgraph_agent


class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("weather")

    
    def run(self, query, session_id):
        tools = {
            "get_weather": weather_tool
        }

        return run_langgraph_agent(query, session_id, tools)