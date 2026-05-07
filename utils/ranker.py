import dotenv
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def rank_news(text):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Rate this AI news from 1 to 10 based on importance and impact. Only return a number."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=5
        )

        score = res.choices[0].message.content.strip()
        return int(score)

    except:
        return 5