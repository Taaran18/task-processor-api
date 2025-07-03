from datetime import timedelta


def format_timestamp(seconds):
    return str(timedelta(seconds=int(seconds)))


def get_file_id(link):
    if "id=" in link:
        return link.split("id=")[-1]
    elif "/d/" in link:
        return link.split("/d/")[1].split("/")[0]
    return None
