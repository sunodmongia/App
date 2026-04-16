import stripe
try:
    from stripe import (
        checkout, 
        billing_portal, 
        webhook, 
        Subscription as StripeSubscriptionResource,
        error as stripe_error
    )
except ImportError:
    checkout = None
    billing_portal = None
    webhook = None
    StripeSubscriptionResource = None
    stripe_error = None

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from subscriptions.models import Subscription, StripeSubscription
from subscriptions.services import (
    assign_subscription,
    create_customer_portal_session,
    create_stripe_checkout_session,
    ensure_default_subscriptions,
    get_user_organization,
    user_can_manage_subscription,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


# ---------------------------------------------------------------------------
# Checkout — redirect to Stripe
# ---------------------------------------------------------------------------

class CheckoutView(LoginRequiredMixin, View):
    """POST: creates a Stripe Checkout Session and redirects to it."""

    def post(self, request, *args, **kwargs):
        ensure_default_subscriptions()

        subscription_pk = request.POST.get("subscription")
        billing_interval = request.POST.get("billing_interval", "monthly")

        subscription = get_object_or_404(
            Subscription.objects.filter(active=True), pk=subscription_pk
        )
        organization = get_user_organization(request.user)

        if not organization:
            messages.error(request, "No organisation found for your account.")
            return redirect("pricing")

        if not user_can_manage_subscription(request.user, organization):
            messages.error(request, "Only the organisation owner can change the plan.")
            return redirect("pricing")

        # Free plan — direct DB update, no Stripe
        if subscription.is_free:
            assign_subscription(organization, subscription)
            # Cancel any active Stripe subscription
            try:
                stripe_sub = organization.stripe_subscription
                if stripe_sub.stripe_subscription_id and StripeSubscriptionResource:
                    StripeSubscriptionResource.cancel(stripe_sub.stripe_subscription_id)
                stripe_sub.status = "canceled"
                stripe_sub.stripe_subscription_id = ""
                stripe_sub.subscription = subscription
                stripe_sub.save()
            except Exception:
                pass
            messages.success(request, f"{organization.name} is now on the Free plan.")
            return redirect("pricing")

        # Paid plan — Stripe Checkout
        success_url = request.build_absolute_uri("/subscriptions/checkout/success/")
        cancel_url = request.build_absolute_uri("/subscriptions/checkout/cancel/")

        session_url, error = create_stripe_checkout_session(
            organization=organization,
            subscription=subscription,
            billing_interval=billing_interval,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        if error:
            messages.error(request, error)
            return redirect("pricing")

        return redirect(session_url)


# ---------------------------------------------------------------------------
# Checkout Success
# ---------------------------------------------------------------------------

class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "subscriptions/checkout_success.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get("session_id")
        if session_id:
            try:
                session = checkout.Session.retrieve(session_id)
                org_id = session.metadata.get("organization_id")
                sub_id = session.metadata.get("subscription_id")
                billing_interval = session.metadata.get("billing_interval", "monthly")

                if org_id and sub_id:
                    from saas.models import Organization
                    org = Organization.objects.get(pk=org_id)
                    plan = Subscription.objects.get(pk=sub_id)

                    assign_subscription(org, plan)

                    # Upsert StripeSubscription record
                    stripe_sub_id = session.subscription or ""
                    StripeSubscription.objects.update_or_create(
                        organization=org,
                        defaults={
                            "subscription": plan,
                            "stripe_subscription_id": stripe_sub_id,
                            "stripe_customer_id": session.customer or "",
                            "billing_interval": billing_interval,
                            "status": "active",
                        },
                    )
            except Exception:
                pass  # Webhook will handle persistent update

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        org = get_user_organization(self.request.user)
        ctx["organization"] = org
        ctx["current_subscription"] = org.subscription if org else None
        return ctx


# ---------------------------------------------------------------------------
# Checkout Cancel
# ---------------------------------------------------------------------------

class CheckoutCancelView(LoginRequiredMixin, TemplateView):
    template_name = "subscriptions/checkout_cancel.html"

    def get(self, request, *args, **kwargs):
        messages.warning(request, "Checkout was cancelled. You have not been charged.")
        return redirect("pricing")


# ---------------------------------------------------------------------------
# Customer Portal
# ---------------------------------------------------------------------------

class CustomerPortalView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        organization = get_user_organization(request.user)
        if not organization:
            messages.error(request, "No organisation found.")
            return redirect("pricing")

        if not user_can_manage_subscription(request.user, organization):
            messages.error(request, "Only the organisation owner can manage billing.")
            return redirect("pricing")

        return_url = request.build_absolute_uri("/pricing/")
        try:
            portal_url = create_customer_portal_session(organization, return_url)
            return redirect(portal_url)
        except Exception as e:
            messages.error(request, f"Could not open billing portal: {e}")
            return redirect("pricing")


# ---------------------------------------------------------------------------
# Stripe Webhook (csrf-exempt, signature verified)
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        if not webhook:
            return HttpResponse("Webhook module missing", status=500)

        try:
            event = webhook.construct_event(payload, sig_header, webhook_secret)
        except (stripe_error.SignatureVerificationError if stripe_error else Exception):
            return HttpResponse("Invalid signature", status=400)
        except Exception:
            return HttpResponse("Bad payload", status=400)

        self._handle_event(event)
        return HttpResponse(status=200)

    def _handle_event(self, event):
        event_type = event["type"]
        data = event["data"]["object"]

        if event_type == "checkout.session.completed":
            self._on_checkout_completed(data)
        elif event_type in ("customer.subscription.updated", "customer.subscription.created"):
            self._on_subscription_updated(data)
        elif event_type == "customer.subscription.deleted":
            self._on_subscription_deleted(data)
        elif event_type == "invoice.payment_succeeded":
            self._on_payment_succeeded(data)

    def _on_checkout_completed(self, session):
        org_id = session.get("metadata", {}).get("organization_id")
        sub_id = session.get("metadata", {}).get("subscription_id")
        billing_interval = session.get("metadata", {}).get("billing_interval", "monthly")
        if not org_id or not sub_id:
            return
        try:
            from saas.models import Organization
            org = Organization.objects.get(pk=org_id)
            plan = Subscription.objects.get(pk=sub_id)
            assign_subscription(org, plan)
            StripeSubscription.objects.update_or_create(
                organization=org,
                defaults={
                    "subscription": plan,
                    "stripe_subscription_id": session.get("subscription", ""),
                    "stripe_customer_id": session.get("customer", ""),
                    "billing_interval": billing_interval,
                    "status": "active",
                },
            )
            # Log revenue event
            from saas.telemetry import Telemetry
            amount_total = (session.get("amount_total") or 0) / 100
            if amount_total > 0:
                Telemetry.revenue(org, amount_total, source="stripe")
        except Exception:
            pass

    def _on_subscription_updated(self, stripe_sub):
        stripe_sub_id = stripe_sub.get("id", "")
        status = stripe_sub.get("status", "incomplete")
        current_period_end = stripe_sub.get("current_period_end")
        try:
            record = StripeSubscription.objects.get(stripe_subscription_id=stripe_sub_id)
            record.status = status
            if current_period_end:
                record.current_period_end = timezone.datetime.fromtimestamp(
                    current_period_end, tz=timezone.utc
                )
            record.save(update_fields=["status", "current_period_end", "updated_at"])
        except StripeSubscription.DoesNotExist:
            pass

    def _on_subscription_deleted(self, stripe_sub):
        stripe_sub_id = stripe_sub.get("id", "")
        try:
            record = StripeSubscription.objects.get(stripe_subscription_id=stripe_sub_id)
            record.status = "canceled"
            record.save(update_fields=["status", "updated_at"])
            # Downgrade org to Free
            free_plan = Subscription.objects.filter(is_default=True, active=True).first()
            if free_plan:
                assign_subscription(record.organization, free_plan)
        except StripeSubscription.DoesNotExist:
            pass

    def _on_payment_succeeded(self, invoice):
        customer_id = invoice.get("customer")
        amount = (invoice.get("amount_paid") or 0) / 100
        try:
            from saas.models import Organization
            org = Organization.objects.get(stripe_customer_id=customer_id)
            from saas.telemetry import Telemetry
            if amount > 0:
                Telemetry.revenue(org, amount, source="stripe")
        except Exception:
            pass
