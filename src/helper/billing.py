import stripe
from stripe import Customer
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_customer(name="", email="", metadata=None, raw=False):
    """Create a Stripe Customer. Returns customer ID by default, or full object if raw=True."""
    response = Customer.create(
        name=name,
        email=email,
        metadata=metadata or {},
    )
    if raw:
        return response
    return response.id


# Legacy alias
Create_Customer = create_stripe_customer
