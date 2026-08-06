#!/usr/bin/env python3
"""Shared Google authentication helpers for Tours Planning."""
import os
from pathlib import Path
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]


def resolve_env_path(env_value: Optional[str], default_relative: str) -> Path:
    candidate = Path(env_value) if env_value else Path(default_relative)
    return candidate if candidate.is_absolute() else ROOT / candidate


def get_google_scopes(scopes: Optional[Iterable[str]] = None) -> list[str]:
    return [scope.strip() for scope in (scopes or DEFAULT_SCOPES) if scope and scope.strip()]


def get_service_account_file() -> Path:
    return resolve_env_path(os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "config/service_account_key.json"), "config/service_account_key.json")


def get_google_credentials(scopes: Optional[Iterable[str]] = None):
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    import google.auth

    scopes = get_google_scopes(scopes)
    service_account_file = get_service_account_file()
    if service_account_file.exists():
        return service_account.Credentials.from_service_account_file(
            str(service_account_file), scopes=scopes
        )

    application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if application_credentials:
        application_credentials_path = resolve_env_path(application_credentials, application_credentials)
        if application_credentials_path.exists():
            try:
                return service_account.Credentials.from_service_account_file(
                    str(application_credentials_path), scopes=scopes
                )
            except ValueError:
                pass

    token_file = resolve_env_path(os.getenv("GOOGLE_TOKEN_FILE", "config/token.json"), "config/token.json")
    credentials_file = resolve_env_path(os.getenv("GOOGLE_CREDENTIALS_FILE", "config/credentials.json"), "config/credentials.json")

    creds = Credentials.from_authorized_user_file(token_file, scopes=scopes) if token_file.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        if credentials_file.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes=scopes)
            creds = flow.run_local_server(port=0)
            token_file.write_text(creds.to_json(), encoding="utf-8")
        else:
            try:
                creds, _ = google.auth.default(scopes=scopes)
            except Exception:
                creds = None
            if creds and getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
                creds.refresh(Request())
            if not creds or not creds.valid:
                raise FileNotFoundError(
                    "No valid Google credentials found. "
                    "Provide config/service_account_key.json, config/credentials.json, or run 'gcloud auth application-default login'."
                )

    return creds
