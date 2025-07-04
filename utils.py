from datetime import timedelta, datetime
import pytz


def format_timestamp(seconds):
    return str(timedelta(seconds=int(seconds)))


def get_file_id(link):
    if "id=" in link:
        return link.split("id=")[-1]
    elif "/d/" in link:
        return link.split("/d/")[1].split("/")[0]
    return None


def get_india_timestamp():
    # Get current UTC time and convert to IST
    utc_now = datetime.utcnow()
    ist = pytz.timezone("Asia/Kolkata")
    ist_now = pytz.utc.localize(utc_now).astimezone(ist)
    return ist_now.strftime("%Y-%m-%d %H:%M:%S")
