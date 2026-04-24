# agent/tools.py
from services.weather_service import get_weather
from services.llm_service import generate_final_response

def handle_tool_call(decision, user_input, request_id):

    tool_name = decision.get("tool_name")
    args = decision.get("arguments", {})

    if tool_name != "get_weather":
        return {"response": "Invalid tool requested"}

    location = args.get("location")

    if not location:
        return {"response": "Location is required"}

    weather_data = get_weather(location)

    final_response = generate_final_response(user_input, weather_data)

    return {"response": final_response}