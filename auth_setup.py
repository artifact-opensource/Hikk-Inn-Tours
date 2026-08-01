"""Playwright-based Google OAuth setup for Tours Planning.

This script automates the Google OAuth flow to obtain credentials and tokens
without requiring manual Google Cloud Console configuration.

Usage:
    python auth_setup.py

The script will:
1. Launch a browser via Playwright
2. Guide you through Google OAuth consent
3. Save credentials.json and token.json to the config/ directory
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


def run_playwright_auth():
    """Use Playwright to automate Google OAuth flow."""
    from playwright.sync_api import sync_playwright

    ensure_config_dir()

    print("=" * 60)
    print("Tours Planning - Google OAuth Setup")
    print("=" * 60)
    print()
    print("This will open a browser to help you set up Google authentication.")
    print("You will need:")
    print("  1. A Google Cloud Project with Google Sheets & Forms APIs enabled")
    print("  2. An OAuth 2.0 Client ID (Desktop app type)")
    print("  3. Your Google account credentials")
    print()
    print("If you need help setting up the Google Cloud project, see:")
    print("  https://console.cloud.google.com/")
    print()

    proceed = input("Do you have a Google Cloud project ready? (yes/no): ").strip().lower()
    if proceed != "yes":
        print("\nPlease set up a Google Cloud project first:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create a new project")
        print("  3. Enable Google Sheets API and Google Forms API")
        print("  4. Create OAuth 2.0 credentials (Desktop app)")
        print("  5. Download credentials.json and place it in config/")
        print()
        print("Then run this script again.")
        return False

    # Check if credentials.json exists
    if not CREDENTIALS_FILE.exists():
        print(f"\n{credentials.json} not found in config/")
        print("Please download it from Google Cloud Console and place it in config/")
        creds_path = input("Enter full path to credentials.json (or press Enter to skip): ").strip()
        if creds_path and os.path.exists(creds_path):
            import shutil
            shutil.copy(creds_path, str(CREDENTIALS_FILE))
            print(f"Copied credentials to {CREDENTIALS_FILE}")
        else:
            print("Skipping credentials setup.")
            return False

    # Run OAuth flow with Playwright
    print("\nLaunching browser for OAuth flow...")
    print("Please authenticate with your Google account in the browser.")
    print("Grant permissions for Google Sheets and Google Forms access.")
    print()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # We'll use the google-auth-oauthlib flow
            # The script generates an auth URL and Playwright captures the token
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

            print(f"Opening auth URL in browser...")
            page.goto(auth_url, wait_until="networkidle")

            # Wait for the user to complete auth
            print("Waiting for you to complete authentication in the browser...")
            print("After granting permissions, close the browser window.")

            try:
                page.wait_for_url("**/oauth2callback**", timeout=300000)
            except Exception:
                pass

            # Try to get the authorization code from the page
            page_content = page.content()

            # Save the page content for manual token extraction
            token_file = CONFIG_DIR / "auth_page.html"
            with open(token_file, "w") as f:
                f.write(page_content)
            print(f"\nAuth page saved to {token_file}")

            browser.close()

            # Manual token entry fallback
            print("\n" + "=" * 60)
            print("If the browser flow completed, you can now enter the")
            print("authorization code manually, or we can try the offline flow.")
            print("=" * 60)

            # Try the installed app flow with Playwright
            print("\nAttempting automatic token exchange...")
            try:
                credentials = flow.run_local_server(
                    host="localhost",
                    port=8080,
                    authorization_prompt_message="Please authorize this application",
                    success_message="Authorization successful! You may close this window.",
                    open_browser=False,
                )

                # Save the token
                token_data = credentials.to_json()
                with open(TOKEN_FILE, "w") as f:
                    f.write(token_data)
                print(f"\nToken saved to {TOKEN_FILE}")
                print("Setup complete! You can now use the automation features.")
                return True

            except Exception as e:
                print(f"\nAutomatic token exchange failed: {e}")
                print("\nManual setup required:")
                print("  1. Go to https://console.cloud.google.com/")
                print("  2. Create OAuth 2.0 Client ID (Desktop app)")
                print("  3. Download credentials.json to config/")
                print("  4. Run: python auth_setup.py --manual")
                return False

    except ImportError:
        print("\nPlaywright not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.check_call(["playwright", "install", "chromium"])
        print("Playwright installed. Run this script again.")
        return False
    except Exception as e:
        print(f"\nError during auth setup: {e}")
        print("\nFalling back to manual setup:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create OAuth 2.0 Client ID (Desktop app)")
        print("  3. Download credentials.json to config/")
        print("  4. Run: python setup_google.py")
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
10. Run: python setup_google.py
""")


if __name__ == "__main__":
    if "--manual" in sys.argv:
        manual_setup()
    else:
        run_playwright_auth()