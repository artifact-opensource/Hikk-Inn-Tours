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
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]


def load_config():
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def authenticate():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    token_file = Path(os.getenv("GOOGLE_TOKEN_FILE", ROOT / "config" / "token.json"))
    credentials_file = Path(os.getenv("GOOGLE_CREDENTIALS_FILE", ROOT / "credentials.json"))
    creds = Credentials.from_authorized_user_file(token_file, SCOPES) if token_file.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not credentials_file.exists():
            raise FileNotFoundError("Download an OAuth client to credentials.json first")
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


def create_spreadsheet(sheets, config):
    body = {"properties": {"title": "Tours Planning Master"}}
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


def create_form(forms):
    destination_names = [item["name"] for item in DESTINATIONS.get("destinations", [])]
    destination_options = destination_names + ["Other", "Flexible / undecided"]


    form = forms.forms().create(body={"info": {
        "title": "Comprehensive Trip Planning & Booking Form",
        "description": "Please provide your trip details, preferences, vehicle requirements, and contact details so our team can customize your complete itinerary."
    }}).execute()

    requests = []
    sections = [
        ("1. Trip Destination & Schedule", [
            choice_item("Which destination are you most interested in?", destination_options, "RADIO", True),
            text_item("Trip Name / Custom Title (optional)", False),
            date_item("Tentative Travel Start Date", True),
            date_item("Tentative Travel End Date", True),
            text_item("Tentative Itinerary / Specific Places You Wish to Visit", False, True)
        ]),
        ("2. Group Demographics", [
            text_item("Number of Adults (18+ years)", True),
            text_item("Number of Children (2-17 years)", False),
            text_item("Number of Infants (0-2 years)", False),
            text_item("Number of Senior Citizens (60+ years)", False)
        ]),
        ("3. Weather & Activities", [
            choice_item("Excursions & Sightseeing Activities", [
                "Skardu Sightseeing", "Hunza Sightseeing", "Deosai Activities",
                "Camel Safari", "K2 Base Camp Climb", "River Rafting"
            ], "CHECKBOX", False),
            choice_item("Equipment Rental Needs", [
                "Tents", "Beds", "Cookware", "Generator", "First Aid Kit"
            ], "CHECKBOX", False),
            text_item("Special Activity Requests", False, True)
        ]),
        ("4. Transportation", [
            text_item("Pickup City / Departure Location", True),
            text_item("Drop-off City / Arrival Location", False)
        ]),
        ("5. Excursions & Equipment Rentals", [
            choice_item("Excursions & Sightseeing Activities", [
                "Skardu Sightseeing", "Hunza Sightseeing", "Deosai Activities",
                "Camel Safari", "K2 Base Camp Climb", "River Rafting"
            ], "CHECKBOX", False),
            choice_item("Equipment Rental Needs", [
                "Tents", "Beds", "Cookware", "Generator", "First Aid Kit"
            ], "CHECKBOX", False)
        ]),
        ("6. Traveler Contact & Emergency Info", [
            text_item("Lead Traveler Full Name", True),
            text_item("Contact Phone (include country code, e.g. +92 300 1234567)", True),
            text_item("Contact Email Address", True),
            text_item("Emergency Contact Full Name", True),
            text_item("Emergency Contact Phone Number", True),
            text_item("Medical Conditions, Allergies, or Dietary Requirements", False, True),
            choice_item("Blood Type", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Unknown"], "RADIO", False)
        ]),
        ("7. Financial & Payment Details", [
            text_item("Estimated Transport Budget (PKR, optional)", False),
            text_item("Initial Deposit Amount (PKR, optional)", False),
            choice_item("Preferred Payment Method", ["Cash", "Card", "Bank Transfer", "Online"], "RADIO", False),
            text_item("Special Requests, Notes, or Accessibility Needs", False, True)
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
    spreadsheet = create_spreadsheet(sheets, config)
    form = create_form(forms)
    print(f"Spreadsheet URL: {spreadsheet['spreadsheetUrl']}")
    print(f"Form ID: {form['formId']}")
    if form.get("responderUri"):
        print(f"Form URL: {form['responderUri']}")
    print("Next: run link_form_responses.gs once in script.google.com to link Form responses to the spreadsheet.")


if __name__ == "__main__":
    main()
