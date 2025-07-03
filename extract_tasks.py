import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def extract_tasks(transcription):
    system_prompt = """
You are an assistant that extracts structured task lists from meeting transcripts.

Generate a Markdown table with these **exact 9 columns**:
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
- Translate tasks if transcript is in Hindi/English mix.
- Break down compound instructions into separate rows.
- Do not return any explanation, only the table.
"""

    user_prompt = f"""Transcript:
{transcription}
"""

    response = openai.ChatCompletion.create(
        model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
    )

    return response["choices"][0]["message"]["content"]
