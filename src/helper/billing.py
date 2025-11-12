import stripe
from decouple import config

DEBUG = config("DEBUG", default=False, cast=bool)
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="", cast=str)

if "sk_test" in STRIPE_SECRET_KEY and not DEBUG:
    raise ValueError("Invalid Payment Key")

stripe.api_key = STRIPE_SECRET_KEY

def Create_Customer(name="", email="", raw=False):
    response = stripe.Customer.create(
        name=name,
        email=email,
    )

    if raw:
        return response
    return response.id
