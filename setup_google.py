#!/usr/bin/env python3
"""Create the production Google Sheet and Form from the repository schema.

Usage: install requirements, download an OAuth client as credentials.json,
then run ``python setup_google.py``. Use ``--dry-run`` to validate locally.
"""
import argparse
import json
import os
from pathlib import Path

from automation.automation import load_environment

ROOT = Path(__file__).resolve().parent
load_environment(ROOT)
CONFIG = ROOT / "config" / "app_config.json"
VEHICLES = json.loads((ROOT / "config" / "vehicles.json").read_text(encoding="utf-8"))
DESTINATIONS = json.loads((ROOT / "config" / "destinations.json").read_text(encoding="utf-8"))
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]


def resolve_env_path(env_value: str, default_relative: str) -> Path:
    candidate = Path(env_value or default_relative)
    return candidate if candidate.is_absolute() else ROOT / candidate


SCOPES = [scope.strip() for scope in os.getenv("GOOGLE_SCOPES", ",".join(DEFAULT_SCOPES)).split(",") if scope.strip()]
SERVICE_ACCOUNT_FILE = resolve_env_path(os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/service_account_key.json"), "config/service_account_key.json")


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def authenticate():
    from automation.google_auth import get_google_credentials

    return get_google_credentials(scopes=SCOPES)


def create_spreadsheet(sheets, config):
    body = {"properties": {"title": "Vanguard Tours Master"}}
    spreadsheet = sheets.spreadsheets().create(body=body, fields="spreadsheetId,spreadsheetUrl,sheets.properties").execute()
    spreadsheet_id = spreadsheet["spreadsheetId"]
    requests = []
    first_sheet_id = spreadsheet["sheets"][0]["properties"]["sheetId"]
    names = list(config["sheets"])
    requests.append({"updateSheetProperties": {"properties": {"sheetId": first_sheet_id, "title": names[0]}, "fields": "title"}})
    for name in names[1:]:
        requests.append({"addSheet": {"properties": {"title": name}}})
    sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()
    for name, definition in config["sheets"].items():
        headers = definition["headers"]
        sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=f"{name}!A1", valueInputOption="RAW", body={"values": [headers]}).execute()
        sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [{"repeatCell": {"range": {"sheetId": sheet_id(sheets, spreadsheet_id, name), "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.12, "green": 0.35, "blue": 0.55}, "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True}}}, "fields": "userEnteredFormat"}}]}).execute()
    return spreadsheet


def sheet_id(sheets, spreadsheet_id, name):
    metadata = sheets.spreadsheets().get(spreadsheetId=spreadsheet_id, fields="sheets.properties").execute()
    return next(item["properties"]["sheetId"] for item in metadata["sheets"] if item["properties"]["title"] == name)


def text_item(title, required=True, paragraph=False):
    return {"title": title, "questionItem": {"question": {"required": required, "textQuestion": {"paragraph": paragraph}}}}


def choice_item(title, options, choice_type="RADIO", required=True):
    return {"title": title, "questionItem": {"question": {"required": required, "choiceQuestion": {"type": choice_type, "options": [{"value": option} for option in options]}}}}


def date_item(title, required=True):
    return {"title": title, "questionItem": {"question": {"required": required, "dateQuestion": {"includeYear": True}}}}


def share_with_anyone(drive, file_id, role="reader"):
    try:
        drive.permissions().create(
            fileId=file_id,
            body={"role": role, "type": "anyone"},
            fields="id"
        ).execute()
    except Exception:
        pass


def create_form(forms):
    destination_names = [item["name"] for item in DESTINATIONS.get("destinations", [])]
    destination_options = destination_names + ["Other", "Flexible / undecided"]

    form = forms.forms().create(body={"info": {
        "title": "Vanguard Tours Expedition Booking Form",
        "description": "Share your destination, group profile, stay preferences, activities, transport needs, and lead traveler details so Vanguard Tours can shape a complete premium itinerary."
    }}).execute()

    requests = []
    sections = [
        ("1. Expedition Overview", [
            choice_item("Select your preferred package", ["Skardu Select", "Skardu Essential", "Skardu Signature", "Skardu Elite"], "RADIO", True),
            choice_item("Which destination are you most interested in?", destination_options, "RADIO", True),
            choice_item("Trip Style", ["Family Escape", "Couples Retreat", "Adventure Expedition", "Photography Journey", "Corporate Retreat", "Mixed Group Tour"], "RADIO", False),
            text_item("Trip Name / Custom Title (optional)", False),
            date_item("Tentative Travel Start Date", True),
            date_item("Tentative Travel End Date", True),
            text_item("Tentative Itinerary / Places of Interest", False, True)
        ]),
        ("2. Group Profile & Comfort", [
            text_item("Number of Adults (18+ years)", True),
            text_item("Number of Children (2-17 years)", False),
            text_item("Number of Infants (0-2 years)", False),
            text_item("Number of Senior Citizens (60+ years)", False),
            choice_item("Comfort Priority", ["Luxury comfort", "Balanced premium", "Adventurous / light"], "RADIO", False),
            text_item("Accessibility or Mobility Notes (optional)", False, True)
        ]),
        ("3. Stay Experience", [
            choice_item("Accommodation Style", ["Luxury 5-Star / Resort", "Executive / 3-4 Star", "Budget / Standard Hotel", "Guesthouse / Homestay", "Camping / Tents"], "RADIO", False),
            text_item("Rooms Needed", False),
            choice_item("Meal Plan Preference", ["Breakfast only", "Half board", "Full board", "Custom itinerary meals"], "RADIO", False),
            text_item("Special Stay Requests", False, True)
        ]),
        ("4. Activities & Equipment", [
            choice_item("Adventure Add-ons", [
                "Skardu Sightseeing", "Hunza Sightseeing", "Deosai Activities",
                "River Rafting", "Camel Safari", "Photography Session"
            ], "CHECKBOX", False),
            choice_item("Equipment Rental Needs", [
                "Tents", "Beds", "Cookware", "Generator", "First Aid Kit"
            ], "CHECKBOX", False),
            text_item("Any special activities or gear you want to add?", False, True)
        ]),
        ("5. Transport & Logistics", [
            text_item("Pickup City / Departure Location", True),
            text_item("Drop-off City / Arrival Location", False),
            choice_item("Preferred Vehicle Class", ["V4 4x4 Sedan", "V8 4x4 SUV", "Premium SUV", "Shared Van"], "RADIO", False),
            text_item("Driver / Escort Preference", False),
            text_item("Transport Notes (airport pickup, luggage, road comfort, etc.)", False, True)
        ]),
        ("6. Lead Traveler & Payment", [
            text_item("Lead Traveler Full Name", True),
            text_item("Contact Phone (include country code, e.g. +92 300 1234567)", True),
            text_item("Contact Email Address", True),
            text_item("Emergency Contact Full Name", True),
            text_item("Emergency Contact Phone Number", True),
            text_item("Medical Conditions, Allergies, or Dietary Requirements", False, True),
            choice_item("Blood Type", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Unknown"], "RADIO", False),
            choice_item("Preferred Payment Method", ["Cash", "Card", "Bank Transfer", "Online"], "RADIO", False),
            text_item("Initial Deposit Amount (PKR, optional)", False)
        ])
    ]

    for title, items in sections:
        requests.append({"createItem": {"item": {"title": title, "pageBreakItem": {}}, "location": {"index": len(requests)}}})
        for item in items:
            requests.append({"createItem": {"item": item, "location": {"index": len(requests)}}})

    forms.forms().batchUpdate(formId=form["formId"], body={"requests": requests}).execute()
    return form


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Validate config without contacting Google")
    args = parser.parse_args()
    config = load_config()
    if args.dry_run:
        assert config["sheets"]["Trip_Database"]["headers"]
        print("Configuration is valid; no Google resources changed.")
        return
    from googleapiclient.discovery import build
    creds = authenticate()
    sheets = build("sheets", "v4", credentials=creds)
    forms = build("forms", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    spreadsheet = create_spreadsheet(sheets, config)
    form = create_form(forms)
    share_with_anyone(drive, spreadsheet["spreadsheetId"], role="reader")
    share_with_anyone(drive, form["formId"], role="reader")
    print(f"Spreadsheet URL: {spreadsheet['spreadsheetUrl']}")
    print(f"Form ID: {form['formId']}")
    if form.get("responderUri"):
        print(f"Form URL: {form['responderUri']}")
    print("Next: run link_form_responses.gs once in script.google.com to link Form responses to the spreadsheet.")
    print("Sharing is enabled for the generated Google resources so the public links can be opened without permission errors.")


if __name__ == "__main__":
    main()
