# agent/fallback.py

import logging
from services.weather_service import get_weather

def fallback_pipeline(user_input: str):

    try:
        return {
            "response": f"Unable to find the result of the user query {user_input}. Please try after some time"
        }

    except Exception as e:
        logging.error(f"Fallback failed: {e}")
        return {
            "response": "Sorry, something went wrong. Please try again."
        }