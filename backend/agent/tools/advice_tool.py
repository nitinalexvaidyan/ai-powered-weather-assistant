from agent.tools.registry import register_tool
from services.response_service import generate_final_response

@register_tool(
    name="weather_advice",
    description="Provide advice based on weather data",
    args_schema={
        "weather_data": "string",
        "user_query": "string"
    }
)
def weather_advice_tool(args, user_input):
    weather_data = args.get("weather_data")
    user_query = args.get("user_query")

    if not weather_data or not user_query:
        return "Error: missing inputs"

    return generate_final_response(user_query, weather_data)