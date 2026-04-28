from agent.tools.registry import register_tool
from services.llm_service import generate_final_response


@register_tool("weather_advice")
def weather_advice_tool(args, user_input):
    weather_data = args.get("weather_data")
    user_query = args.get("user_query")

    if not weather_data or not user_query:
        return "Error: missing inputs"

    return generate_final_response(user_query, weather_data)