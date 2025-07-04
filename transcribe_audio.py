import tempfile, os, requests
import openai
import ffmpeg
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

    suffix = ".oga"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_audio:
        tmp_audio.write(response.content)
        tmp_audio_path = tmp_audio.name

    # Convert to .mp3 before transcription
    converted_path = tmp_audio_path.replace(suffix, ".mp3")
    try:
        ffmpeg.input(tmp_audio_path).output(converted_path).run(
            overwrite_output=True, quiet=True
        )
        print("🔁 Converted .oga to .mp3:", converted_path)
    except Exception as e:
        print("❌ ffmpeg conversion failed:", e)
        raise e

    print("📥 Whisper transcription started for:", converted_path)
    try:
        with open(converted_path, "rb") as audio_file:
            transcript_response = openai.Audio.translate("whisper-1", audio_file)
            print("📝 Whisper response:", transcript_response)
    except Exception as e:
        print("❌ Whisper failed:", e)
        raise e
    finally:
        os.remove(tmp_audio_path)
        os.remove(converted_path)

    transcription_text = transcript_response.get("text", "").strip()
    if not transcription_text:
        raise Exception("Whisper returned empty transcription.")

    return transcription_text, source_link
