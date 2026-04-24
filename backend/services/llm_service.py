# services/llm_service.py
import json
import requests
import os
import logging
from dotenv import load_dotenv
from utils.parser import safe_parse_json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# -------------------------------
# 🔹 Core Gemini Caller (Reusable)
# -------------------------------
def call_gemini(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, json=payload, timeout=5)
    response.raise_for_status()

    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']


# -------------------------------
# 🔹 Agent Decision (with Retry)
# -------------------------------
def agent_decision(user_input: str, retries: int = 2) -> dict:
    prompt = build_agent_prompt(user_input)

    for attempt in range(retries + 1):
        try:
            raw_text = call_gemini(prompt)
            logging.info(f"[LLM RAW] {raw_text}")

            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = safe_parse_json(cleaned_text)

            if not parsed:
                raise ValueError("Invalid JSON from LLM")

            logging.info(f"[LLM PARSED] {parsed}")
            return parsed

        except Exception as e:
            logging.warning(f"LLM attempt {attempt} failed: {e}")

    raise Exception("LLM failed after retries")


# -------------------------------
# 🔹 Final Response Generator
# -------------------------------
def generate_final_response(user_input: str, weather_data: dict) -> str:
    try:
        prompt = build_final_response_prompt(user_input, weather_data)
        raw_text = call_gemini(prompt)
        return raw_text.strip()

    except Exception as e:
        logging.error(f"Final response generation failed: {e}")
        return "I couldn't format the weather response properly, but here's the data."
    


# -------------------------------
# 🔹 Prompt Builders
# -------------------------------
def build_agent_prompt(user_input: str) -> str:
    return f"""
        You are an AI assistant that decides whether to call a tool or respond directly.

        You must ALWAYS return valid JSON.
        Do NOT return text outside JSON.

        Available Tools:

        1. get_weather
        Description: Get weather for a city
        Arguments:
            - location (string)

        Output formats:

        1. Tool call:
        {{
        "action": "call_tool",
        "tool_name": "get_weather",
        "arguments": {{
            "location": "<city>"
        }}
        }}

        2. Direct response:
        {{
        "action": "respond",
        "message": "<message>"
        }}

        Rules:
        - Always return valid JSON
        - If city missing → ask user
        - Only weather-related queries allowed

        User Query: "{user_input}"
    """


def build_final_response_prompt(user_input: str, weather_data: dict) -> str:
    return f"""
        User asked:
        "{user_input}"

        Weather data:
        {json.dumps(weather_data)}

        Generate a simple, human-friendly weather response.
        Keep it short.
    """