import pytest
from weather_api import fetch_weather
import os

def test_weather_api_key_set():
    """Test that API key is configured."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    assert api_key, "OPENWEATHER_API_KEY environment variable not set"

def test_fetch_weather():
    """Test weather API call."""
    if not os.getenv("OPENWEATHER_API_KEY"):
        pytest.skip("API key not set")
    
    result = fetch_weather("London")
    assert "London" in result or "weather" in result.lower()
    assert "Error" not in result

def test_fetch_weather_invalid_city():
    """Test weather API with invalid city."""
    if not os.getenv("OPENWEATHER_API_KEY"):
        pytest.skip("API key not set")
    
    result = fetch_weather("InvalidCityName12345")
    assert "Failed" in result or "Error" in result



