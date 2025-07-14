import os
import requests
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from config import GOOGLE_CREDENTIALS_BASE64, FOLDER_ID


def upload_to_drive(file_url):
    # Step 1: Download the audio file
    response = requests.get(file_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download file from {file_url}")

    content_type = response.headers.get("Content-Type", "")
    ext = ".oga" if "ogg" in content_type else ".mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    # Step 2: Decode credentials from environment variable
    import base64, json

    creds_json = base64.b64decode(GOOGLE_CREDENTIALS_BASE64).decode("utf-8")
    creds_dict = json.loads(creds_json)

    creds = Credentials.from_service_account_info(
        creds_dict, scopes=["https://www.googleapis.com/auth/drive"]
    )

    # Step 3: Build Drive API client
    service = build("drive", "v3", credentials=creds)

    filename = os.path.basename(tmp_file_path)
    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID],  # 👈 Must be a folder inside a Shared Drive
    }

    media = MediaFileUpload(tmp_file_path, resumable=True)

    # Step 4: Upload the file
    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    file_id = file.get("id")

    # Step 5: Build and return the file's shared Drive URL
    drive_link = f"https://drive.google.com/file/d/{file_id}/view"
    os.remove(tmp_file_path)  # Clean up
    return drive_link
