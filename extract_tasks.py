import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def extract_tasks(transcription):
    system_prompt = """
You are an assistant that extracts structured task information from either:
- informal natural language (like WhatsApp voice notes)
- OR structured field-based formats like:
  Task Description: ...
  Employee Name: ...
  Target Date: ...

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
- Support both free-form speech and field-style input.
- Treat field-style data as a direct task.
- If any field is missing, use "None".
- Never write explanations. Only return the markdown table.
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
