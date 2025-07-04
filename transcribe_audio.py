import tempfile, os, requests
import openai
from utils import get_file_id
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def transcribe_audio(gdrive_url):
    file_id = get_file_id(gdrive_url)
    if not file_id:
        raise ValueError("Invalid Google Drive link.")

    source_link = f"https://drive.google.com/file/d/{file_id}/view"
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(download_url)

    if "html" in response.headers.get("Content-Type", ""):
        raise Exception("Invalid or private Google Drive audio file.")

    # ✅ Extract extension from the download URL
    ext = os.path.splitext(download_url)[-1] or ".mp3"  # fallback to mp3

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_audio:
        tmp_audio.write(response.content)
        tmp_audio_path = tmp_audio.name

    with open(tmp_audio_path, "rb") as audio_file:
        transcript_response = openai.Audio.translate("whisper-1", audio_file)

    os.remove(tmp_audio_path)
    transcription_text = transcript_response.get("text", "")
    return transcription_text, source_link