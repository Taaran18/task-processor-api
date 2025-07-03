from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from transcribe_audio import transcribe_audio
from transcribe_text import transcribe_text
from extract_tasks import extract_tasks
from parse_output import parse_structured_output
from write_output import write_to_sheet, log_whatsapp_message

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
        else:  # text
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
        payload = await request.json()
        message = payload.get("message", "")
        sender = payload.get("from_number", "")

        if message.lower().startswith("/task "):
            command_text = message[6:]

            # ✅ Log the message in the TEXT_INPUT_SHEET
            log_whatsapp_message(command_text)

            transcription = command_text
            structured_output = extract_tasks(transcription)
            rows = parse_structured_output(structured_output, "text", transcription)
            write_to_sheet(rows)

            return {
                "status": "✅ Task processed from WhatsApp",
                "tasks_added": len(rows),
                "from": sender,
            }

        return {
            "status": "ignored",
            "reason": "No /task trigger in message",
            "from": sender,
        }

    except Exception as e:
        return {"error": str(e)}
