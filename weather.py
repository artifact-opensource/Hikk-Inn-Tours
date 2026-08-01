"""Weather details per date using Open-Meteo API (free, no key required)."""
import requests
from datetime import date, datetime
from typing import List, Optional, Dict, Any

WEATHER_BASE = "https://api.open-meteo.com/v1/forecast"


def get_weather_for_location(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> List[Dict[str, Any]]:
    """Fetch daily weather forecasts for a date range at a lat/lon point.

    Returns a list of daily records with temperature, wind, precipitation, and conditions.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,uv_index_max",
        "timezone": "auto",
        "forecast_days": 16,
    }
    resp = requests.get(WEATHER_BASE, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    daily = data.get("daily", {})
    times = daily.get("time", [])
    records = []
    for i, day in enumerate(times):
        records.append(
            {
                "date": day,
                "weather_code": daily.get("weather_code", [None])[i],
                "temp_max_c": daily.get("temperature_2m_max", [None])[i],
                "temp_min_c": daily.get("temperature_2m_min", [None])[i],
                "precip_mm": daily.get("precipitation_sum", [None])[i],
                "wind_kph": daily.get("wind_speed_10m_max", [None])[i],
                "uv_index": daily.get("uv_index_max", [None])[i],
            }
        )
    return records


def get_weather_for_dates(
    latitude: float,
    longitude: float,
    dates: List[str],
) -> List[Dict[str, Any]]:
    """Fetch weather for a specific list of date strings (YYYY-MM-DD)."""
    if not dates:
        return []
    sorted_dates = sorted(dates)
    start = sorted_dates[0]
    end = sorted_dates[-1]
    all_records = get_weather_for_location(latitude, longitude, start, end)
    date_set = set(dates)
    return [r for r in all_records if r["date"] in date_set]


WEATHER_CODES = {
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
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


def describe_weather(code: Optional[int]) -> str:
    """Return a human-readable weather description from a WMO weather code."""
    if code is None:
        return "Unknown"
    return WEATHER_CODES.get(code, f"Code {code}")
