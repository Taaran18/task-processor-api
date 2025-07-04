from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import tempfile

FOLDER_ID = "1G_glXXIf_mjTjk7UwZlbGf6k9H-NiuPB"  # Your Drive folder ID


def upload_to_drive(media_url):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # Download audio file
    response = requests.get(media_url)
    if response.status_code != 200:
        raise Exception("Failed to download audio from WhatsApp")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    # Upload to Drive
    file_drive = drive.CreateFile(
        {"parents": [{"id": FOLDER_ID}], "title": "whatsapp_audio.ogg"}
    )
    file_drive.SetContentFile(tmp_path)
    file_drive.Upload()

    # Return public Drive link
    return f"https://drive.google.com/file/d/{file_drive['id']}/view"
