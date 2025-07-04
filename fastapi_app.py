from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from transcribe_audio import transcribe_audio
from transcribe_text import transcribe_text
from extract_tasks import extract_tasks
from parse_output import parse_structured_output
from write_output import write_to_sheet, log_whatsapp_message  # ✅ new import
from google_drive_uploader import upload_to_drive  # You’ll create this

app = FastAPI()


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
async def receive_whatsapp(request: Request):
    try:
        data = await request.json()
        print("📩 Raw Maytapi payload:", data)

        message = data.get("message", {})
        message_type = message.get("type", "")
        mime_type = message.get("mimetype", "")
        sender = data.get("user", {}).get("phone", "")

        # ✅ TEXT TASK
        message_text = message.get("text", "")
        command_text = message_text.strip()

        if message_type == "text" and (
            command_text.lower().startswith("/task ")
            or command_text.lower().startswith("task ")
        ):
            if command_text.lower().startswith("/task "):
                command_text = command_text[6:]
            elif command_text.lower().startswith("task "):
                command_text = command_text[5:]

            log_whatsapp_message(command_text)
            structured_output = extract_tasks(command_text)
            rows = parse_structured_output(structured_output, "text", command_text)
            write_to_sheet(rows)

            return {"status": "✅ Text task processed", "tasks_added": len(rows)}

        # ✅ AUDIO TASK (as document with audio/mpeg)
        if message_type == "document" and mime_type.startswith("audio/"):
            media_url = message.get("url")
            if not media_url:
                return {"status": "error", "reason": "No audio URL found"}  

            # Download and upload to Drive
            gdrive_url = upload_to_drive(media_url)

            # Transcribe and process
            transcription, source_link = transcribe_audio(gdrive_url)
            structured_output = extract_tasks(transcription)
            rows = parse_structured_output(structured_output, "audio", source_link)
            write_to_sheet(rows)

            return {"status": "✅ Audio task processed", "tasks_added": len(rows)}

        return {
            "status": "ignored",
            "reason": "Not a valid task or unsupported media",
            "from": sender,
        }

    except Exception as e:
        print("❌ Webhook Error:", str(e))
        return {"error": str(e)}
