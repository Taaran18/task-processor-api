import gspread
from google.oauth2 import service_account
from config import SERVICE_ACCOUNT_FILE, SCOPES


def authorize():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return gspread.authorize(creds)
