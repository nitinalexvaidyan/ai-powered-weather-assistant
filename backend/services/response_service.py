# services/response_service.py

import json
from services.llm_service import call_gemini


def generate_final_response(user_input: str, weather_data: dict) -> str:
    prompt = f"""
        User: {user_input}
        Data: {json.dumps(weather_data)}

        Give a short, clear weather answer.
    """

    return call_gemini(prompt).strip()