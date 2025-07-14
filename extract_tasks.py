import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def extract_tasks(transcription):
    system_prompt = """
You are an assistant that extracts structured task lists from WhatsApp messages or voice transcripts.

The input may be:
- A paragraph, like: "Assign Apurvi to create a media plan by 14 July."
- Or a bullet/field format, like:
  Task Description: Create a media plan
  Employee Name: Apurvi Jain
  Target Date: 14-7
  Priority: Medium

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
- Handle casual Hindi-English mix as well.
- If any detail is missing, write "None" in that column.
- Break down multiple tasks into separate rows if found.
- DO NOT include explanations, summaries, or anything other than the markdown table.
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
