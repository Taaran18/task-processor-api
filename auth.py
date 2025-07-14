import os
import base64
import tempfile
import gspread
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def authorize():
    encoded = os.getenv("GOOGLE_CREDENTIALS_BASE64")
    if not encoded:
        raise ValueError("Missing GOOGLE_CREDENTIALS_BASE64 environment variable")

    creds_data = base64.b64decode(encoded).decode("utf-8")

    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as tmp:
        tmp.write(creds_data)
        tmp_path = tmp.name

    creds = service_account.Credentials.from_service_account_file(
        tmp_path, scopes=SCOPES
    )
    return gspread.authorize(creds)
