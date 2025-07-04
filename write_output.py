from auth import authorize
from config import OUTPUT_SHEET_ID
from utils import get_india_timestamp

def write_to_sheet(rows):
    if not rows:
        return
    client = authorize()
    sheet = client.open_by_key(OUTPUT_SHEET_ID).sheet1
    sheet.append_rows(rows, value_input_option="USER_ENTERED")
