from groq import Groq
from decouple import config
import re

client = Groq(api_key=config("GROQ_API_KEY"))

def format_response(text):
    """Format bot response with HTML for better display"""
    # Convert bold important terms
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Convert markdown links to HTML <a> tags
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#667eea;text-decoration:underline">\1</a>', text)
    return text.strip()

def ask_groq(history, company_context):
    """
    Core function to communicate with Groq AI.
    Consolidates system prompting, template enforcement, and response formatting.
    """
    system_message = {
        "role": "system",
        "content": f"""
You are WireTech's official AI customer support assistant. 

### MISSION
Provide helpful, accurate answers using ONLY the information provided in the Knowledge Base below.

### KNOWLEDGE BASE
{company_context}

### CORE RULES
1. Do NOT use external knowledge. 
2. Do NOT guess or invent information. 
3. If information is missing, say: "I'm not able to find that specific detail. Please contact support@wiretech.com for further assistance."
4. Maintain a professional, polite, and helpful tone.
5. No emojis. Use clear, simple language.
6. Look at the whole conversation context when answering follow-up questions.

### OUTPUT FORMAT (MANDATORY)
Every response MUST strictly follow this Markdown structure:

**[Topic Name]**

**Overview**
A 1-2 sentence high-level summary.

**Details**
- Use clear bullet points for features, pricing, or steps.
- Put each item on its own line.

**Note**
Optional section for specific conditions (e.g., refund windows, setup time).

### SPECIAL INSTRUCTIONS (PRICING & CONTACT)
- Always mention both Monthly and Annual pricing if both are available.
- Mention the ~20% savings on annual plans when relevant.
- Clearly state that the Free plan requires no credit card.
- IMPORTANT: If providing an email or phone number, MUST format as a Markdown link, e.g., `[support@wiretech.com](mailto:support@wiretech.com)` and `[+91-800-555-0199](tel:+91-800-555-0199)`.
"""
    }

    # Prepend the system directive to the conversation history
    messages = [system_message] + history
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2, # Low temperature for high factual accuracy
            max_tokens=500,
        )
        response = completion.choices[0].message.content
        return format_response(response)
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again or contact support! 😔"
