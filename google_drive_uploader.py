import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile
import os

FOLDER_ID = "1G_glXXIf_mjTjk7UwZlbGf6k9H-NiuPB"


def upload_to_drive(media_url):
    creds = service_account.Credentials.from_service_account_file(
        "credentials.json", scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=creds)

    # Download the audio file
    response = requests.get(media_url)
    if response.status_code != 200:
        raise Exception("Failed to download file")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    # Upload to Google Drive
    file_metadata = {"name": os.path.basename(tmp_path), "parents": [FOLDER_ID]}
    media = MediaFileUpload(tmp_path, mimetype="audio/mpeg")
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    os.remove(tmp_path)

    file_id = uploaded.get("id")
    return f"https://drive.google.com/file/d/{file_id}/view"
