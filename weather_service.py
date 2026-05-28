"""Shared real-weather logic for the Weather MCP project.

This file does not know anything about MCP or Streamlit.
It only knows how to:
1. Find a location.
2. Fetch weather from Open-Meteo.
3. Return beginner-friendly Python dictionaries.
"""

import sys

import requests


# Open-Meteo geocoding API.
# This API converts a place name like "London" into latitude and longitude.
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"


# Open-Meteo forecast API.
# This API uses latitude and longitude to return real weather data.
FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"


# Some users search for states or regions instead of cities.
# Open-Meteo geocoding is strongest for cities, so this small fallback map
# helps beginner users get a useful answer for common region searches.
FALLBACK_LOCATIONS = {
    "rajasthan": {
        "name": "Rajasthan",
        "latitude": 27.0238,
        "longitude": 74.2179,
        "admin1": "Rajasthan",
        "country": "India",
    },
}


# Weather codes are numbers returned by Open-Meteo.
# This dictionary converts those numbers into beginner-friendly text.
WEATHER_CODE_TO_CONDITION = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def safe_print(message: str):
    """Print messages safely in Windows terminals with limited encoding."""

    safe_message = message.encode("ascii", errors="backslashreplace").decode("ascii")

    print(safe_message, file=sys.stderr)


def get_weather_icon(condition: str):
    """Choose a simple icon name based on the condition text."""

    condition_text = condition.lower()

    if "clear" in condition_text or "sun" in condition_text:
        return "sun"
    if "cloud" in condition_text or "overcast" in condition_text:
        return "cloud"
    if "rain" in condition_text or "drizzle" in condition_text:
        return "rain"
    if "snow" in condition_text:
        return "snow"
    if "thunderstorm" in condition_text:
        return "storm"
    if "fog" in condition_text:
        return "fog"

    return "mixed"


def find_location(place: str):
    """Find a city or fallback region using Open-Meteo geocoding."""

    safe_print(f"Weather Service: Searching location database for: {place}")

    geocoding_params = {
        "name": place,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = requests.get(GEOCODING_API_URL, params=geocoding_params, timeout=10)
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if results:
        location = results[0]
        safe_print(f'Weather Service: Location found: {location["name"]}')
        return location

    fallback_location = FALLBACK_LOCATIONS.get(place.lower())

    if fallback_location is not None:
        safe_print(f"Weather Service: Fallback location found for: {place}")
        return fallback_location

    safe_print(f"Weather Service: No location found for: {place}")
    return None


def fetch_current_weather(latitude: float, longitude: float):
    """Fetch real current weather and 5-day forecast."""

    safe_print(f"Weather Service: Fetching weather for: {latitude}, {longitude}")

    forecast_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 5,
        "timezone": "auto",
    }

    response = requests.get(FORECAST_API_URL, params=forecast_params, timeout=10)
    response.raise_for_status()

    return response.json()


def build_location_name(location: dict):
    """Build a readable location name from a geocoding result."""

    name_parts = [location["name"]]

    if "admin1" in location and location["admin1"] != location["name"]:
        name_parts.append(location["admin1"])

    if "country" in location:
        name_parts.append(location["country"])

    return ", ".join(name_parts)


def get_weather_data(place: str):
    """Return real current weather and 5-day forecast for a place."""

    place_name = place.strip()

    if not place_name:
        return {
            "success": False,
            "message": "Please enter a city or place name.",
        }

    try:
        location_result = find_location(place_name)

        if location_result is None:
            return {
                "success": False,
                "city": place_name,
                "message": f"Sorry, I could not find weather for {place_name}.",
            }

        weather_result = fetch_current_weather(
            location_result["latitude"],
            location_result["longitude"],
        )
    except requests.exceptions.RequestException:
        safe_print("Weather Service: Weather API request failed.")

        return {
            "success": False,
            "city": place_name,
            "message": "Weather API is not reachable right now. Please try again.",
        }

    current_weather = weather_result["current"]
    temperature = current_weather["temperature_2m"]
    weather_code = current_weather["weather_code"]
    condition = WEATHER_CODE_TO_CONDITION.get(weather_code, "Unknown condition")
    humidity = current_weather["relative_humidity_2m"]
    wind_speed = current_weather["wind_speed_10m"]
    location = build_location_name(location_result)
    daily_weather = weather_result["daily"]
    forecast = []

    for index, forecast_date in enumerate(daily_weather["time"]):
        forecast_code = daily_weather["weather_code"][index]
        forecast_condition = WEATHER_CODE_TO_CONDITION.get(forecast_code, "Unknown condition")

        forecast.append(
            {
                "date": forecast_date,
                "max_temperature": f'{daily_weather["temperature_2m_max"][index]}\u00b0C',
                "min_temperature": f'{daily_weather["temperature_2m_min"][index]}\u00b0C',
                "condition": forecast_condition,
                "icon": get_weather_icon(forecast_condition),
            }
        )

    safe_print(f"Weather Service: Weather data ready for {location}.")

    return {
        "success": True,
        "city": location_result["name"],
        "location": location,
        "latitude": location_result["latitude"],
        "longitude": location_result["longitude"],
        "temperature": f"{temperature}\u00b0C",
        "condition": condition,
        "icon": get_weather_icon(condition),
        "humidity": f"{humidity}%",
        "wind_speed": f"{wind_speed} km/h",
        "forecast": forecast,
    }


def get_temperature_data(place: str):
    """Return only the current temperature for a place."""

    weather_result = get_weather_data(place)

    if not weather_result["success"]:
        return weather_result

    return {
        "success": True,
        "city": weather_result["city"],
        "location": weather_result["location"],
        "temperature": weather_result["temperature"],
    }
