# services/llm_service.py

import requests
import os
import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
logging.info(f"GEMINI_API_KEY: {GEMINI_API_KEY}")

import requests
import json
import logging

def extract_weather_intent(user_input: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

    prompt = f"""
You are a JSON API.
Extract structured data from the user query below.
User Query: "{user_input}"
Return ONLY a valid JSON object with this exact schema:
{{
  "location": string,
  "date": "today" | "tomorrow" | string,
  "intent": string
}}

STRICT RULES:
- Do NOT add markdown (no ```json)
- Do NOT add explanation
- Do NOT add extra text
- Output must be valid JSON parsable by json.loads()

Example:
{{
  "location": "Bangalore",
  "date": "today",
  "intent": "rain"
}}
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()

        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        logging.info(f"[LLM RAW] {text}")

        clean_text = text.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(clean_text)
        logging.info(f"[LLM PARSED] {parsed}")

        # ✅ Validate structure
        validated = validate_intent(parsed)
        return validated

    except Exception as e:
        logging.error(f"LLM failed: {e}")

        # ✅ Fallback (VERY IMPORTANT)
        return fallback_intent(user_input)


def validate_intent(data: dict):
    required_keys = ["location", "date", "intent"]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key: {key}")

    return {
        "location": str(data["location"]),
        "date": str(data["date"]),
        "intent": str(data["intent"])
    }

def fallback_intent(user_input: str):
    # Very basic rule-based fallback
    user_input = user_input.lower()

    location = "Bangalore"  # default fallback

    if "mumbai" in user_input:
        location = "Mumbai"
    elif "delhi" in user_input:
        location = "Delhi"

    return {
        "location": location,
        "date": "today",
        "intent": "weather"
    }