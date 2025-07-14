from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from extract_tasks import extract_tasks
from parse_output import parse_structured_output
from write_output import write_to_sheet
from transcribe_audio import transcribe_audio
from google_drive_uploader import upload_to_drive

app = FastAPI()


# ✅ Process text immediately — write directly to output sheet
def process_text_task(text):
    structured_output = extract_tasks(text)
    rows = parse_structured_output(
        structured_output, "text", text
    )  # 'text' used as source link
    write_to_sheet(rows)


# ✅ Process audio by uploading, transcribing, and writing results
def process_audio_task(media_url):
    try:
        print("🎧 Starting voice/audio task:", media_url)

        gdrive_url = upload_to_drive(media_url)
        print("✅ Uploaded to Drive:", gdrive_url)

        transcription, source_link = transcribe_audio(gdrive_url)
        print("📝 Transcription:", transcription[:300])

        structured_output = extract_tasks(transcription)
        print("📋 Extracted Tasks Output:", structured_output[:300])

        rows = parse_structured_output(structured_output, "audio", source_link)
        print(f"✅ Parsed {len(rows)} tasks")

        write_to_sheet(rows)
        print("📤 Sheet updated.")

    except Exception as e:
        print("❌ process_audio_task error:", str(e))


# 🧪 For manual testing via Postman or other clients
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
            transcription = text_input
            source_link = text_input

        structured_output = extract_tasks(transcription)
        rows = parse_structured_output(structured_output, choice, source_link)
        write_to_sheet(rows)
        return {"message": f"{len(rows)} structured tasks added."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Webhook endpoint for WhatsApp via Maytapi
@app.post("/webhook")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        print("📩 Payload:", data)

        message = data.get("message", {})
        message_type = message.get("type", "")
        mime_type = message.get("mime", "")
        media_url = message.get("url")
        message_text = message.get("text", "")
        sender = data.get("user", {}).get("phone", "")

        # ✅ Process /task text messages directly — write to output sheet
        if message_type == "text" and message_text:
            command_text = message_text.strip()
            if command_text.lower().startswith(
                "/task "
            ) or command_text.lower().startswith("task "):
                command_text = (
                    command_text[6:]
                    if command_text.lower().startswith("/task ")
                    else command_text[5:]
                )
                background_tasks.add_task(process_text_task, command_text)
                return {"status": "✅ Text task received", "from": sender}

        # ✅ Handle voice recording (ptt)
        if message_type == "ptt" and mime_type.startswith("audio/"):
            if not media_url:
                return {"status": "error", "reason": "No audio URL for voice message"}
            background_tasks.add_task(process_audio_task, media_url)
            return {"status": "✅ Voice recording received", "from": sender}

        # ✅ Handle audio file (as document)
        if message_type == "document" and mime_type.startswith("audio/"):
            if not media_url:
                return {"status": "error", "reason": "No audio URL for document"}
            background_tasks.add_task(process_audio_task, media_url)
            return {"status": "✅ Audio file received", "from": sender}

        return {"status": "ignored", "reason": "No task trigger", "from": sender}

    except Exception as e:
        print("❌ Webhook error:", str(e))
        return {"error": str(e)}
