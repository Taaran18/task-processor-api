from fastapi import FastAPI, HTTPException, Request ,BackgroundTasks
from pydantic import BaseModel
from transcribe_audio import transcribe_audio
from transcribe_text import transcribe_text
from extract_tasks import extract_tasks
from parse_output import parse_structured_output
from write_output import write_to_sheet, log_whatsapp_message  # ✅ new import
from google_drive_uploader import upload_to_drive  # You’ll create this


app = FastAPI()


def process_text_task(text):
    log_whatsapp_message(text)
    structured_output = extract_tasks(text)
    rows = parse_structured_output(structured_output, "text", text)
    write_to_sheet(rows)

def process_audio_task(media_url):
    try:
        print("🎧 Starting process_audio_task with URL:", media_url)

        gdrive_url = upload_to_drive(media_url)
        print("✅ Uploaded to Drive:", gdrive_url)

        transcription, source_link = transcribe_audio(gdrive_url)
        print("📝 Transcription complete.")

        structured_output = extract_tasks(transcription)
        print("📋 Task extraction complete.")

        rows = parse_structured_output(structured_output, "audio", source_link)
        print(f"✅ Parsed {len(rows)} rows.")

        write_to_sheet(rows)
        print("📤 Written to sheet.")

    except Exception as e:
        print("❌ Error in process_audio_task:", str(e))


class ProcessRequest(BaseModel):
    choice: str  # "audio" or "text"
    gdrive_url: str | None = None
    text_input: str | None = None


@app.post("/process")
def process(req: ProcessRequest):
    choice = req.choice.strip().lower()
    gdrive_url = req.gdrive_url.strip() if req.gdrive_url else ""
    text_input = req.text_input.strip() if req.text_input else ""
    source_link = ""

    if choice not in ["audio", "text"]:
        raise HTTPException(
            status_code=400, detail="Invalid choice. Use 'audio' or 'text'."
        )

    try:
        if choice == "audio":
            if not gdrive_url:
                raise HTTPException(
                    status_code=400, detail="Missing Google Drive URL for audio choice."
                )
            transcription, source_link = transcribe_audio(gdrive_url)

        elif choice == "text":
            transcription = text_input if text_input else transcribe_text()
            source_link = transcription

        structured_output = extract_tasks(transcription)
        rows = parse_structured_output(structured_output, choice, source_link)
        write_to_sheet(rows)
        return {"message": f"{len(rows)} structured tasks added."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        message = data.get("message", {})
        message_type = message.get("type", "")
        mime_type = message.get("mime", "")
        message_text = message.get("text", "")
        sender = data.get("user", {}).get("phone", "")

        # ✅ TEXT task
        if message_type == "text" and "task" in message_text.lower():
            command_text = message_text.strip()
            command_text = command_text[6:] if command_text.lower().startswith("/task ") else command_text[5:]
            background_tasks.add_task(process_text_task, command_text)
            return {"status": "✅ Task received", "from": sender}

        # ✅ AUDIO task (document)
        if message_type == "document" and mime_type.startswith("audio/"):
            media_url = message.get("url")
            background_tasks.add_task(process_audio_task, media_url)
            return {"status": "✅ Audio task received", "from": sender}

        return {"status": "ignored", "reason": "No task trigger", "from": sender}

    except Exception as e:
        return {"error": str(e)}