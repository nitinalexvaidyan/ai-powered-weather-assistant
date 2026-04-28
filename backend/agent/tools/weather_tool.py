from agent.tools.registry import register_tool
from services.weather_service import get_weather


@register_tool("get_weather")
def weather_tool(args, user_input):
    location = args.get("location")

    if not location:
        return "Error: location missing"

    return get_weather(location)