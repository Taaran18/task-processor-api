from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transcribe_audio import transcribe_audio
from transcribe_text import transcribe_text
from extract_tasks import extract_tasks
from parse_output import parse_structured_output
from write_output import write_to_sheet

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

        structured_output = extract_tasks(transcription)
        rows = parse_structured_output(structured_output, choice, source_link)
        write_to_sheet(rows)
        return {"message": f"{len(rows)} structured tasks added."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
