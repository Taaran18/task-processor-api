import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def extract_tasks(transcription):
    system_prompt = """
You are an assistant that extracts structured task lists from WhatsApp messages.

Users may send either:
1. A paragraph describing the task (e.g., "Assign API testing to Rahul...")
2. A form-like message with fields (e.g., "Task Description: ...", "Employee Name: ...")

✅ Your job:
- Generate a Markdown table with these **exact 9 columns**:
  1. Task Description  
  2. Employee Name  
  3. Target Date  
  4. Priority (High/Medium/Low/Urgent)  
  5. Approval Needed (Yes/No)  
  6. Client Name  
  7. Department  
  8. Comments  
  9. Assigned By

⚠️ Instructions:
- If some fields are missing, leave the cell blank.
- If values are in Hindi or mixed language, translate them.
- Never output any explanation — just the table.
"""

    user_prompt = f"""Transcript:
{transcription}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )
    return response["choices"][0]["message"]["content"]
