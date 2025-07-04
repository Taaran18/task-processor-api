from datetime import datetime
import pytz
from auth import authorize
from config import TEXT_INPUT_SHEET_ID


def transcribe_text():
    client = authorize()
    sheet = client.open_by_key(TEXT_INPUT_SHEET_ID).sheet1
    all_rows = sheet.get_all_values()
    transcript_lines = []

    # Force timestamp to GMT+5:30 using pytz localization
    utc = pytz.utc
    ist = pytz.timezone("Asia/Kolkata")
    now_utc = datetime.utcnow()
    now_ist = utc.localize(now_utc).astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")

    for i, row in enumerate(all_rows, start=1):
        text = row[0].strip() if len(row) > 0 else ""
        status = row[1].strip().lower() if len(row) > 1 else ""
        if text and status != "done":
            transcript_lines.append(text)
            sheet.update_cell(i, 2, "DONE")
            sheet.update_cell(i, 3, now_ist)

    if not transcript_lines:
        raise ValueError("No new transcript lines found.")
    return "\n".join(transcript_lines)
