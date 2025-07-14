import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def extract_tasks(transcription):
    system_prompt = """
You are an assistant that extracts structured task details from two types of user input:
1. Casual/natural language (e.g. WhatsApp voice or paragraph text)
2. Field-based task entries (e.g., 'Task Description: ...', 'Employee Name: ...')

🎯 Your job is to extract all tasks and convert them into a markdown table with these 9 columns:
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
- Always generate a markdown table.
- Accept both paragraph and key:value formats.
- If any column is missing, fill with "None".
- Never return explanations — only the table.
"""


    user_prompt = f"""Transcript:
{transcription}
"""

    response = openai.ChatCompletion.create(
        model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return response["choices"][0]["message"]["content"]
