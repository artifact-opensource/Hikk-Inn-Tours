import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from weather import get_weather_for_location
from automation.automation import load_environment

load_environment(Path(__file__).resolve().parents[1])


DESTINATION_COORDINATES = {
    "skardu": (35.2880, 75.5362),
    "hunza": (36.3205, 74.9899),
    "shigar": (35.2250, 75.4200),
    "khaplu": (35.4167, 76.2236),
    "deosai": (35.0249, 75.4469),
    "fairy meadows": (35.1611, 74.6536),
}


def _get_query_params(request):
    if hasattr(request, "args") and request.args is not None:
        return {k: request.args.get(k) for k in request.args}
    if hasattr(request, "query") and request.query is not None:
        return {k: request.query.get(k) for k in request.query}
    if hasattr(request, "url") and request.url:
        parsed = urlparse(request.url)
        return {k: v[0] for k, v in parse_qs(parsed.query).items()}
    return {}


def handler(request):
    params = _get_query_params(request)
    dest = str(params.get("dest", "")).strip()
    start_date = str(params.get("start", "")).strip()
    end_date = str(params.get("end", "")).strip()
    if not dest or not start_date or not end_date:
        return {"error": "dest, start, and end are required"}, 400, {"Content-Type": "application/json"}

    coords = DESTINATION_COORDINATES.get(dest.strip().lower())
    if not coords:
        coords = (35.0, 75.0)

    try:
        weather = get_weather_for_location(coords[0], coords[1], start_date, end_date)
        return weather, 200, {"Content-Type": "application/json"}
    except Exception as exc:
        return {"error": str(exc)}, 500, {"Content-Type": "application/json"}
