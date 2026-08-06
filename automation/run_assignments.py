#!/usr/bin/env python3
"""Scan Trip_Database for pending trips, consolidate by destination+date, and assign fleet.

Usage: set `TOURS_SPREADSHEET_ID`, ensure credentials.json and token.json exist, then run.
"""
import logging
import os
from pathlib import Path

from googleapiclient.discovery import build

from automation.automation import ToursPlannerAutomation, load_environment

ROOT = Path(__file__).resolve().parent.parent
load_environment(ROOT)
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def resolve_env_path(env_value: str, default_relative: str) -> Path:
    candidate = Path(env_value or default_relative)
    return candidate if candidate.is_absolute() else ROOT / candidate


def authenticate():
    from automation.google_auth import get_google_credentials

    return get_google_credentials(scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ])


def main():
    spreadsheet_id = os.getenv("TOURS_SPREADSHEET_ID")
    if not spreadsheet_id:
        raise RuntimeError("Set TOURS_SPREADSHEET_ID environment variable to the spreadsheet id")
    creds = authenticate()
    sheets = build("sheets", "v4", credentials=creds)
    automation = ToursPlannerAutomation(sheets_service=sheets, spreadsheet_id=spreadsheet_id)
    # read Trip_Database to discover pending destination+date groups
    config = automation.load_configuration() or {}
    headers = config.get("sheets", {}).get("Trip_Database", {}).get("headers", [])
    resp = sheets.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range="Trip_Database!A2:Z").execute()
    rows = resp.get("values", [])
    groups = {}
    for r in rows:
        row = {headers[i]: (r[i] if i < len(r) else "") for i in range(len(headers))}
        if row.get("trip_status", "").strip().lower() in ("pending", "", "pending"):
            key = (row.get("destination", "").strip(), row.get("check_in_date", "").strip())
            if key[0] and key[1]:
                groups.setdefault(key, 0)
                groups[key] += int(row.get("total_guests", 0) or 0)
    for (destination, date_iso), total in groups.items():
        LOGGER.info("Consolidating %s guests for %s on %s", total, destination, date_iso)
        result = automation.consolidate_and_assign(destination, date_iso)
        LOGGER.info("Result: %s", result)


if __name__ == "__main__":
    main()
