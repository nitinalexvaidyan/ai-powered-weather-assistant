# services/response_service.py

import json
from services.llm_service import call_gemini


def generate_final_response(user_input: str, weather_data: dict) -> str:
    try:
        prompt = f"""
            User: {user_input}
            Data: {json.dumps(weather_data)}

            Give a short, clear weather answer.
        """

        return call_gemini(prompt, cache_ttl=900).strip()
    except Exception:
        # 🔥 Fallback (no LLM)
        return fallback_response(weather_data)
    

def fallback_response(weather_data):
    try:
        temp = weather_data.get("main", {}).get("temp")
        condition = weather_data.get("weather", [{}])[0].get("main")

        return f"Temperature is {temp}°C with {condition} conditions."

    except:
        return "Weather data available, but unable to format response."