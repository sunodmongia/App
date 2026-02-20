from groq import Groq
from decouple import config
import re

client = Groq(api_key=config("GROQ_API_KEY"))

def format_response(text):
    """Format bot response with HTML for better display"""
    # Convert numbered lists
    text = re.sub(r'^(\d+\.\s)', r'<br><strong>\1</strong>', text, flags=re.MULTILINE)
    # Convert bullet points
    text = re.sub(r'^[•\-]\s', r'<br>• ', text, flags=re.MULTILINE)
    # Bold important terms
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Convert email to clickable link
    text = re.sub(r'(support@wiretech\.com)', r'<a href="mailto:\1" style="color:#667eea;text-decoration:underline">\1</a>', text)
    # Convert phone to clickable link
    text = re.sub(r'(\+91-800-555-0199)', r'<a href="tel:\1" style="color:#667eea;text-decoration:underline">\1</a>', text)
    return text.strip()

def ask_groq(message, company_context):
    messages = [
    {
        "role": "system",
        "content": f"""
You are Wire's friendly AI customer support assistant.

Your mission: Provide helpful, accurate answers using ONLY the information below.
Never guess or make up information.

{company_context}

RESPONSE STYLE:
- Be warm, friendly, and conversational
- Use emojis sparingly (1-2 per response)
- Keep responses concise (2-4 sentences for simple queries)
- Use bullet points for lists
- Bold important information using **text**
- End with a helpful follow-up question when appropriate

FORMATTING RULES:
- Use numbered lists (1. 2. 3.) for steps or multiple items
- Use bullet points (•) for features or options
- Break long responses into short paragraphs
- Highlight prices, emails, and phone numbers

ESCALATION:
- For account issues, billing problems, or technical errors → provide support@wiretech.com
- For refunds after 7 days → politely explain policy and offer support email
- For abuse/illegal requests → politely decline

IF UNKNOWN:
Say: "I don't have that information right now. Please contact **support@wiretech.com** or call **+91-800-555-0199** for assistance! 📞"
"""
    },
    {
        "role": "user",
        "content": message
    }
]
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.5,
        max_tokens=400,
    )

    response = completion.choices[0].message.content
    return format_response(response)
