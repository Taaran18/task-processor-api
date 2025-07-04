import os
import tempfile
import base64
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

FOLDER_ID = os.getenv("FOLDER_ID")  # not hardcoded



def upload_to_drive(media_url):
    # ✅ Decode base64 credentials from env
    encoded = os.getenv("GOOGLE_CREDENTIALS_BASE64")
    if not encoded:
        raise Exception("Missing GOOGLE_CREDENTIALS_BASE64 environment variable")

    creds_data = base64.b64decode(encoded).decode("utf-8")

    # ✅ Write to a temp file
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json") as tmp:
        tmp.write(creds_data)
        tmp_path = tmp.name

    # ✅ Load credentials
    creds = service_account.Credentials.from_service_account_file(
        tmp_path, scopes=["https://www.googleapis.com/auth/drive"]
    )

    drive_service = build("drive", "v3", credentials=creds)

    # ✅ Download the file from WhatsApp media URL
    response = requests.get(media_url)
    if response.status_code != 200:
        raise Exception("Failed to download audio from WhatsApp")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
        audio_file.write(response.content)
        audio_path = audio_file.name

    # ✅ Upload to Drive
    file_metadata = {"name": os.path.basename(audio_path), "parents": [FOLDER_ID]}
    media = MediaFileUpload(audio_path, mimetype="audio/mpeg")
    uploaded = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    os.remove(audio_path)
    os.remove(tmp_path)

    file_id = uploaded.get("id")
    return f"https://drive.google.com/file/d/{file_id}/view"
