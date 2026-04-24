# services/llm_service.py
import json
import time
import requests
import os
import logging
from dotenv import load_dotenv
from utils.parser import safe_parse_json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# -------------------------------
# 🔹 Core Gemini Caller (with retry + backoff)
# -------------------------------
def call_gemini(prompt: str, retries=3) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-preview:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=5)

            if response.status_code == 429:
                wait = 2 * (attempt + 1)
                logging.warning(f"Rate limit hit. Retrying in {wait}s...")
                time.sleep(wait)
                continue

            response.raise_for_status()

            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']

        except Exception as e:
            logging.error(f"Gemini call failed (attempt {attempt}): {e}")
            time.sleep(1)

    raise Exception("Gemini failed after retries")


# -------------------------------
# 🔹 Agent Decision
# -------------------------------
def agent_decision(context: str, retries: int = 1) -> dict:
    prompt = build_agent_prompt(context)

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
            logging.warning(f"LLM decision attempt {attempt} failed: {e}")

    raise Exception("LLM decision failed after retries")


# -------------------------------
# 🔹 Final Response Generator
# -------------------------------
def generate_final_response(user_input: str, weather_data: str) -> str:
    try:
        prompt = build_final_response_prompt(user_input, weather_data)
        raw_text = call_gemini(prompt)
        return raw_text.strip()

    except Exception as e:
        logging.error(f"Final response generation failed: {e}")
        return "I couldn't process the advice properly, but weather data is available."


# -------------------------------
# 🔹 Prompt Builders
# -------------------------------
def build_agent_prompt(context: str) -> str:
    return f"""
You are an AI assistant that decides whether to call a tool or respond directly.

You must ALWAYS return valid JSON.
Do NOT return text outside JSON.

Available Tools:

1. get_weather
Description: Get weather for a city
Arguments:
- location (string)

2. weather_advice
Description: Provide advice based on weather data and user query
Arguments:
- weather_data (string)
- user_query (string)

Output formats:

1. Tool call:
{{
  "action": "call_tool",
  "tool_name": "<tool_name>",
  "arguments": {{ ... }}
}}

2. Direct response:
{{
  "action": "respond",
  "message": "<message>"
}}

Rules:
- Always return valid JSON
- Use get_weather when weather data is needed
- Use weather_advice when user asks for suggestions
- If weather data is already available, DO NOT call get_weather again
- Do NOT call the same tool repeatedly
- Prefer responding if sufficient information is available
- If required info is missing → ask user

Conversation so far:
{context}

Decide the next action.
"""


def build_final_response_prompt(user_input: str, weather_data: str) -> str:
    return f"""
User asked:
"{user_input}"

Weather data:
{weather_data}

Provide clear, short advice.
"""