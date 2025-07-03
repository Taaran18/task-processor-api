from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from transcribe_audio import transcribe_audio
from transcribe_text import transcribe_text
from extract_tasks import extract_tasks
from parse_output import parse_structured_output
from write_output import write_to_sheet, log_whatsapp_message  # ✅ new import

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

        # ✅ Navigate to the correct nested structure
        body = data.get("body", {})
        message_data = body.get("message", {})
        message_text = message_data.get("text", "")

        sender = body.get("user", {}).get("phone", "")

        # ✅ Check that message_text is a string and starts with /task
        if isinstance(message_text, str) and message_text.strip().lower().startswith("/task "):
            command_text = message_text.strip()[6:]  # Remove "/task "

            # ✅ Log raw message to TEXT_INPUT_SHEET_ID
            log_whatsapp_message(command_text)

            # ✅ Process it into structured tasks
            structured_output = extract_tasks(command_text)
            rows = parse_structured_output(structured_output, "text", command_text)
            write_to_sheet(rows)

            return {
                "status": "✅ Task processed from WhatsApp",
                "tasks_added": len(rows),
                "from": sender
            }

        return {
            "status": "ignored",
            "reason": "No /task trigger in message or bad format",
            "from": sender
        }

    except Exception as e:
        return {"error": str(e)}
