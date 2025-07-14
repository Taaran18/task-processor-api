import re
import pandas as pd
from io import StringIO
from utils import get_india_timestamp, generate_task_id


def parse_structured_output(markdown_text, input_type, source):
    """
    Parses GPT's markdown table output and returns structured rows
    ready for appending to Google Sheets.
    """
    rows = []

    # Try to extract markdown table using regex
    table_match = re.search(r"\|(.+\|)+\n\|([-:| ]+)\n((?:\|.*\n)+)", markdown_text)
    if table_match:
        header = table_match.group(1)
        body = table_match.group(3)
        raw_table = f"|{header}\n|{'---|' * (header.count('|'))}\n{body}"
        try:
            df = pd.read_csv(
                StringIO(raw_table), sep="|", engine="python", skipinitialspace=True
            )
            df = df.dropna(how="all", axis=1).dropna(how="all", axis=0)
            df.columns = [col.strip() for col in df.columns]

            for _, row in df.iterrows():
                rows.append(
                    {
                        "Timestamp": get_india_timestamp(),
                        "Task ID": generate_task_id(),
                        "Task Description": row.get("Task Description", "None").strip(),
                        "Employee Name": row.get("Employee Name", "None").strip(),
                        "Employee Email ID": "None",
                        "Target Date": row.get("Target Date", "None").strip(),
                        "Priority": row.get("Priority", "None").strip(),
                        "Approval Needed": row.get("Approval Needed", "None").strip(),
                        "Client Name": row.get("Client Name", "None").strip(),
                        "Department": row.get("Department", "None").strip(),
                        "Assigned Name": row.get("Assigned By", "None").strip(),
                        "Assigned Email ID": "None",
                        "Comments": row.get("Comments", "None").strip(),
                        "Source Link": source,
                    }
                )

        except Exception as e:
            print("❌ Error parsing markdown table:", str(e))

    # Fallback if no table parsed or GPT missed formatting
    if not rows:
        print("⚠️ No markdown table found. Using fallback row.")
        rows.append(
            {
                "Timestamp": get_india_timestamp(),
                "Task ID": generate_task_id(),
                "Task Description": "None",
                "Employee Name": "None",
                "Employee Email ID": "None",
                "Target Date": "None",
                "Priority": "None",
                "Approval Needed": "None",
                "Client Name": "None",
                "Department": "None",
                "Assigned Name": "None",
                "Assigned Email ID": "None",
                "Comments": "None",
                "Source Link": source.strip(),
            }
        )

    return rows
