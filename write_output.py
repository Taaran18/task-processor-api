from auth import authorize
from config import SPREADSHEET_ID, TEXT_INPUT_SHEET_ID


def write_to_sheet(rows):
    client = authorize()
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    for row in rows:
        print("⬇️ Writing row to sheet:", row)
        sheet.append_row(row)


def log_whatsapp_message(message_text):
    client = authorize()
    sheet = client.open_by_key(TEXT_INPUT_SHEET_ID).sheet1
    sheet.append_row([message_text])
