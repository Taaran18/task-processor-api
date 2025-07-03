from auth import authorize
from config import SPREADSHEET_ID


def write_to_sheet(rows):
    client = authorize()
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    for row in rows:
        sheet.append_row(row)
