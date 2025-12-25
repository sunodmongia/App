from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def ask_groq(message, company_context):
    messages = [
        {
            "role": "system",
            "content": f"You are a professional customer support assistant.\n\nCompany info:\n{company_context}"
        },
        {
            "role": "user",
            "content": message
        }
    ]

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.4,
        max_tokens=300,
    )

    return completion.choices[0].message.content
