from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from .groq_client import ask_groq
from .knowledge_base import get_company_context

@api_view(["POST"])
@ensure_csrf_cookie
def chatbot(request):
    user_message = request.data.get("message")

    if not user_message:
        return Response({"error": "Message required"}, status=400)
    
    context = get_company_context()
    reply = ask_groq(user_message, context)

    return Response({"user": user_message, "bot": reply})
