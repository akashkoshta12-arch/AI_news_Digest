from groq import Groq
from dotenv import load_dotenv
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def generate_thought():
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Generate a short inspiring tech thought or insight about AI in 1 line."
                }
            ],
            max_tokens=50
        )

        return res.choices[0].message.content.strip()

    except:
        return "AI is shaping the future faster than we imagine 🚀"