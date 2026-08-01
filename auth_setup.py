"""Playwright-based Google OAuth setup for Tours Planning.

This script helps set up Google authentication for the Tours Planning
application using Playwright browser automation.

Usage:
    python auth_setup.py

The script will:
1. Launch a browser via Playwright
2. Guide you through Google OAuth consent
3. Save credentials.json and token.json to the config/ directory

Prerequisites:
    - A Google Cloud Project with Google Sheets & Forms APIs enabled
    - An OAuth 2.0 Client ID (Desktop app type) downloaded as credentials.json
    - Place credentials.json in the config/ directory before running
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "config"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"


def ensure_config_dir():
    CONFIG_DIR.mkdir(exist_ok=True)


def check_credentials():
    """Check if credentials.json exists and is valid."""
    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: {CREDENTIALS_FILE} not found.")
        print("\nPlease download credentials.json from Google Cloud Console:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Select your project")
        print("  3. Go to APIs & Services > Credentials")
        print("  4. Create OAuth 2.0 Client ID (Desktop app)")
        print("  5. Download and rename to credentials.json")
        print("  6. Place it in the config/ directory")
        return False
    return True


def run_oauth_flow():
    """Run the OAuth flow using Playwright."""
    ensure_config_dir()

    if not check_credentials():
        return False

    print("=" * 60)
    print("Tours Planning - Google OAuth Setup")
    print("=" * 60)
    print()
    print("This will open a browser to help you authenticate with Google.")
    print("You will need to grant permissions for Google Sheets and Forms.")
    print()

    from google_auth_oauthlib.flow import Flow

    CLIENT_SECRETS = str(CREDENTIALS_FILE)
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/drive.file",
    ]

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )

    print("Starting OAuth flow...")
    print("A browser window will open for you to authenticate.")
    print("Please sign in with your Google account and grant permissions.")
    print()

    try:
        credentials = flow.run_local_server(
            host="localhost",
            port=8080,
            authorization_prompt_message="Please authorize this application",
            success_message="Authorization successful! You may close this window.",
            open_browser=True,
        )

        # Save the token
        token_data = credentials.to_json()
        with open(TOKEN_FILE, "w") as f:
            f.write(token_data)
        print(f"\nToken saved to {TOKEN_FILE}")
        print("Setup complete! You can now use the automation features.")
        return True

    except Exception as e:
        print(f"\nOAuth flow error: {e}")
        print("\nFalling back to manual setup...")
        manual_setup()
        return False


def manual_setup():
    """Guide user through manual Google Cloud setup."""
    print("\n" + "=" * 60)
    print("Manual Google Cloud Setup Guide")
    print("=" * 60)
    print("""
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable these APIs:
   - Google Sheets API
   - Google Forms API
   - Google Drive API
4. Go to APIs & Services > Credentials
5. Create Credentials > OAuth 2.0 Client ID
6. Application type: Desktop app
7. Name it "Tours Planning"
8. Download the JSON file
9. Rename it to credentials.json and place in config/
10. Run: python auth_setup.py
""")


def run_playwright_browser_auth():
    """Use Playwright to automate the browser-based OAuth flow."""
    ensure_config_dir()

    if not check_credentials():
        return False

    print("=" * 60)
    print("Tours Planning - Playwright Browser Auth")
    print("=" * 60)
    print()
    print("This will open a browser to help you authenticate.")
    print("After granting permissions, the token will be saved automatically.")
    print()

    from playwright.sync_api import sync_playwright
    from google_auth_oauthlib.flow import Flow

    CLIENT_SECRETS = str(CREDENTIALS_FILE)
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/drive.file",
    ]

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            print("Opening browser for authentication...")
            page.goto(auth_url, wait_until="networkidle")

            # Wait for user to complete auth
            print("Please authenticate in the browser window.")
            print("After granting permissions, the setup will continue automatically.")
            print("(Or close the browser window when done.)")

            try:
                page.wait_for_url("**/oauth2callback**", timeout=300000)
                print("Authorization callback detected!")
            except Exception:
                print("Timeout waiting for callback. Trying manual token entry...")

            browser.close()

        # Try to exchange the code for a token
        try:
            credentials = flow.run_local_server(
                host="localhost",
                port=8080,
                authorization_prompt_message="Please authorize",
                success_message="Success!",
                open_browser=False,
            )
            token_data = credentials.to_json()
            with open(TOKEN_FILE, "w") as f:
                f.write(token_data)
            print(f"\nToken saved to {TOKEN_FILE}")
            return True
        except Exception:
            print("\nAutomatic token exchange failed.")
            manual_setup()
            return False

    except Exception as e:
        print(f"\nBrowser auth error: {e}")
        manual_setup()
        return False


if __name__ == "__main__":
    if "--manual" in sys.argv:
        manual_setup()
    elif "--browser" in sys.argv:
        run_playwright_browser_auth()
    else:
        # Try the full flow
        run_oauth_flow()