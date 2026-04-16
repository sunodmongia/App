from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from .groq_client import ask_groq
from .knowledge_base import get_company_context
from subscriptions.services import get_user_organization


@api_view(["POST"])
@ensure_csrf_cookie
def chatbot(request):
    # Support both legacy "message" string and new "history" array
    user_message = request.data.get("message")
    history = request.data.get("history")

    if not history:
        if not user_message:
            return Response({"error": "Message or history required"}, status=400)
        # Convert legacy single message to history format
        history = [{"role": "user", "content": user_message}]

    # Try to grab the current user's organization to inject personalized context
    organization = None
    if request.user.is_authenticated:
        organization = get_user_organization(request.user)

    context = get_company_context(user=request.user if request.user.is_authenticated else None, org=organization)

    reply = ask_groq(history, context)

    return Response({
        "user_message_count": len(history), 
        "context_used": context, 
        "bot": reply
    })
