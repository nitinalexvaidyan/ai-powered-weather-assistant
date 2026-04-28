from agents.weather.agent import WeatherAgent
from agents.aqi.agent import AQIAgent

weather_agent = WeatherAgent()
aqi_agent = AQIAgent()

class RouterAgent:
    def route(self, query: str, session_id: str):
        text = query.lower()

        if any(word in text for word in ["aqi", "air", "pollution"]):
            return aqi_agent.run(query, session_id)

        return weather_agent.run(query, session_id)