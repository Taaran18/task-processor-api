import openai
import re
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def is_field_format(text):
    return bool(re.search(r"(?i)^\s*[\w\s]+:\s*.+", text.strip(), re.MULTILINE))


def extract_tasks(transcription):
    if is_field_format(transcription):
        return convert_field_input_to_markdown(transcription)
    else:
        return extract_with_gpt(transcription)


def convert_field_input_to_markdown(text):
    fields = {
        "Task Description": "None",
        "Employee Name": "None",
        "Target Date": "None",
        "Priority": "None",
        "Approval Needed": "None",
        "Client Name": "None",
        "Department": "None",
        "Comments": "None",
        "Assigned By": "None",
    }

    for line in text.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            for f in fields:
                if key.lower() == f.lower():
                    fields[f] = value
                    break

    row = "| " + " | ".join(fields[f] for f in fields) + " |"
    header = "| " + " | ".join(fields.keys()) + " |"
    separator = "| " + " | ".join(["---"] * len(fields)) + " |"

    return f"{header}\n{separator}\n{row}"


def extract_with_gpt(transcription):
    system_prompt = """
You are an assistant that extracts structured task details from casual speech, such as WhatsApp voice messages or informal audio.

🎯 Your job is to extract tasks and organize them into a markdown table with these exact 9 columns:
1. Task Description  
2. Employee Name  
3. Target Date  
4. Priority (High/Medium/Low/Urgent)  
5. Approval Needed (Yes/No)  
6. Client Name  
7. Department  
8. Comments  
9. Assigned By

✅ Guidelines:
- Support casual and mixed Hindi-English phrasing (e.g., "Assign the API testing to Ravi by Friday").
- Split multiple tasks into separate rows.
- If any detail is missing, use "None" in that column.
- Do NOT include any explanation, intro, or summary — only the markdown table.
"""

    user_prompt = f"""Transcript:
{transcription}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response["choices"][0]["message"]["content"]
