from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def stripe_webhook(request):
    """Deprecated: webhook is now handled by StripeWebhookView in subscriptions app."""
    return HttpResponse(status=200)
