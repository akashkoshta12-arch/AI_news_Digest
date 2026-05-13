from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def summarize(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Summarize this tech news in 2 bullet points. Return ONLY plain text."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.5,
            max_tokens=150
        )

        result = response.choices[0].message.content

        #  CLEAN OUTPUT (IMPORTANT)
        result = result.replace("*", "").strip()

        return result

    except Exception as e:
        print("ERROR:", e)
        return "Summary not available"