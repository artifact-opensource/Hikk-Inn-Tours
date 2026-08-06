import json
from pathlib import Path

from automation.automation import ToursPlannerAutomation, load_environment

load_environment(Path(__file__).resolve().parents[1])

def _parse_json_request(request):
    if hasattr(request, "json"):
        try:
            return request.json()
        except Exception:
            pass
    if hasattr(request, "get_json"):
        try:
            return request.get_json()
        except Exception:
            pass
    body = None
    if hasattr(request, "body"):
        body = request.body
    elif hasattr(request, "data"):
        body = request.data
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="ignore")
    if isinstance(body, str) and body.strip():
        try:
            return json.loads(body)
        except ValueError:
            pass
    return {}


def handler(request):
    payload = _parse_json_request(request)
    automation = ToursPlannerAutomation()
    result = automation.process_form_submission(payload)
    status_code = 200 if result.get("status") != "error" else 400
    response = {"status": result.get("status"), "data": result.get("data"), "result": result.get("result")}
    if result.get("error"):
        response["error"] = result.get("error")
    return response, status_code, {"Content-Type": "application/json"}
