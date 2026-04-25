import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(prompt):
    if not GROQ_API_KEY:
        return "ERROR: GROQ_API_KEY is missing. Add it to your .env file or hosting secrets."

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are AcaIntel AI, a careful RAG assistant. Answer only from retrieved context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=700
        )

        return response.choices[0].message.content.strip()

    except Exception as error:
        return f"ERROR: Generation failed: {error}"