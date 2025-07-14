import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def extract_tasks(transcription):
    system_prompt = """
You are an assistant that extracts structured task lists from either paragraph text or field-style messages.

The input may look like:
1. A paragraph describing one or more tasks
2. A list of labeled fields like:
   Task Description: ...
   Employee Name: ...
   Target Date: ...

You must always extract the tasks into a Markdown table with exactly these 9 columns:
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
- Translate Hindi/English mix if needed.
- Parse as many tasks as you can.
- If only one task is found, output one row.
- Never return explanations, only the markdown table.
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
