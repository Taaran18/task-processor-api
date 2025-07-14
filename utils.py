from datetime import datetime
import pytz
import uuid


def get_india_timestamp():
    india = pytz.timezone("Asia/Kolkata")
    return datetime.now(india).strftime("%d/%m/%Y %H:%M:%S")


def generate_task_id():
    return str(uuid.uuid4())[:8]
