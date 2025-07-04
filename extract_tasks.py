import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def extract_tasks(transcription):
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
        model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return response["choices"][0]["message"]["content"]
