import requests
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_aqi_tool(args):
    location = args.get("location")

    if not location:
        return "Location missing"

    # Step 1: Get lat/lon
    geo_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}"
    geo_res = requests.get(geo_url).json()

    lat = geo_res["coord"]["lat"]
    lon = geo_res["coord"]["lon"]

    # Step 2: AQI
    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    aqi_res = requests.get(aqi_url).json()

    return aqi_res