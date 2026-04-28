# agent/tools.py
from services.weather_service import get_weather
from services.llm_service import generate_final_response

def execute_tool(decision, user_input):
    tool_name = decision.get("tool_name")
    args = decision.get("arguments", {})

    if tool_name == "get_weather":
        location = args.get("location")

        if not location:
            return "Error: location missing"

        return get_weather(location)

    elif tool_name == "weather_advice":
        weather_data = args.get("weather_data")
        user_query = args.get("user_query") or user_input

        if not weather_data or not user_query:
            return "Error: missing inputs"

        return generate_final_response(user_query, weather_data)

    else:
        return "Error: Unknown tool"