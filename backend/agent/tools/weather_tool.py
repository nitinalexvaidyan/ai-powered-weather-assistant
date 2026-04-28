from agent.tools.registry import register_tool
from services.weather_service import get_weather
from services.cache_service import get_cache, set_cache


@register_tool(
    name="get_weather",
    description="Get weather for a city",
    args_schema={"location": "string"}
)
def weather_tool(args, user_input):
    location = args.get("location")

    if not location:
        return "Error: location missing"

    cache_key = f"weather:{location.lower()}"

    # 🔥 Step 1: Check cache
    cached = get_cache(cache_key)
    if cached:
        print(f"[CACHE HIT] {cache_key}")
        return cached
    else:
        print(f"[CACHE MISS] {cache_key}")

    # 🔥 Step 2: Call API
    result = get_weather(location)

    # 🔥 Step 3: Store in cache
    set_cache(cache_key, result)

    return result