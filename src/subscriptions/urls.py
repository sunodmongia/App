from django.urls import path
from subscriptions.views import (
    CheckoutView,
    CheckoutSuccessView,
    CheckoutCancelView,
    CustomerPortalView,
    StripeWebhookView,
)

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="subscription-checkout"),
    path("checkout/success/", CheckoutSuccessView.as_view(), name="subscription-checkout-success"),
    path("checkout/cancel/", CheckoutCancelView.as_view(), name="subscription-checkout-cancel"),
    path("portal/", CustomerPortalView.as_view(), name="subscription-portal"),
    path("webhook/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
