# main.py

from fastapi import FastAPI
from services.llm_service import extract_weather_intent
from services.weather_service import get_weather
import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def home():
    logging.info("DEBUG: inside API")
    return {"success": True, "message": "Welcome to homepage"}


@app.get("/weather")
def weather(query: str):
    # Step 1: Extract intent
    intent_data = extract_weather_intent(query)
    logging.info(f"intent_data: {intent_data}")

    location = intent_data.get("location")

    # Step 2: Get weather
    weather_data = get_weather(location)
    logging.info(f"weather_data: {weather_data}")


    # Step 3: Format response (basic)
    temp = weather_data["main"]["temp"]
    description = weather_data["weather"][0]["description"]

    return {
        "location": location,
        "temperature": temp,
        "description": description
    }