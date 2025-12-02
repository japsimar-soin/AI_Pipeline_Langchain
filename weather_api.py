import os
from langsmith import traceable
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


@traceable
def fetch_weather(city: str) -> str:
    """Fetch weather data from OpenWeatherMap API."""
    if not OPENWEATHER_API_KEY:
        return "Error: OpenWeatherMap API key not set. Please set OPENWEATHER_API_KEY environment variable."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Failed to fetch weather. Status code: {response.status_code}"

        data = response.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        return f"""Weather in {city}:
- Description: {weather_desc}
- Temperature: {temp}°C (feels like {feels_like}°C)
- Humidity: {humidity}%"""
    except Exception as e:
        return f"Error fetching weather: {str(e)}"
