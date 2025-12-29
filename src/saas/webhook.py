import json
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Organization
from saas.telemetry import Telemetry

stripe.api_key = "YOUR_STRIPE_SECRET_KEY"

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = stripe.Event.construct_from(
        json.loads(payload), stripe.api_key
    )

    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]

        customer_id = invoice["customer"]
        amount = invoice["amount_paid"] / 100  # Stripe uses cents

        # Map Stripe customer → Organization
        org = Organization.objects.get(stripe_customer_id=customer_id)

        Telemetry.revenue(org, amount)

    return HttpResponse(status=200)
