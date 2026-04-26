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

        data = get_weather(location)

        # 🔥 Trim + structure output (VERY IMPORTANT)
        try:
            return f"Temp={data['main']['temp']}°C, Humidity={data['main']['humidity']}%, Condition={data['weather'][0]['description']}"
        except Exception:
            return "Weather data unavailable"

    elif tool_name == "weather_advice":
        weather_data = args.get("weather_data")
        user_query = args.get("user_query") or user_input

        if not weather_data:
            return "Error: missing weather data for advice"

        return generate_final_response(user_query, weather_data)

    else:
        return "Error: Unknown tool"
    

