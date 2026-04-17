import stripe
try:
    from stripe import checkout, billing_portal, Customer
except ImportError:
    checkout = None
    billing_portal = None
    Customer = None

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Permission
from django.db import transaction

from subscriptions.models import (
    PlanLimit,
    SUBSCRIPTION_PERMISSIONS,
    Subscription,
    StripeSubscription,
)

stripe.api_key = settings.STRIPE_SECRET_KEY

# ---------------------------------------------------------------------------
# Dynamic Subscription Engine
# ---------------------------------------------------------------------------

# Valid slugs are now determined by what exists in the database
def get_valid_plan_slugs():
    return set(Subscription.objects.values_list("slug", flat=True))


# ---------------------------------------------------------------------------
# Plan bootstrap
# ---------------------------------------------------------------------------

def get_active_subscriptions():
    """
    Returns all active subscriptions with their limits.
    Does NOT modify the database. This is the main runtime helper.
    """
    return Subscription.objects.filter(active=True).select_related("planlimit").order_by(
        "display_order", "monthly_price", "id"
    )


def ensure_default_subscriptions(force=False):
    """
    One-time bootstrap or forced sync for canonical plans.
    If 'force' is False, it will NOT touch existing plans if any exist.
    """
    if not force and Subscription.objects.filter(active=True).exists():
        return get_active_subscriptions()

def ensure_default_subscriptions(force=False):
    """
    Returns active plans. 
    Bootstrapping is now managed via management commands or manual admin entries
    to prevent hardcoded overrides.
    """
    return get_active_subscriptions()


def get_default_subscription():
    return (
        Subscription.objects.filter(active=True, is_default=True)
        .select_related("planlimit")
        .order_by("display_order", "id")
        .first()
    ) or (
        Subscription.objects.filter(active=True)
        .select_related("planlimit")
        .order_by("display_order", "id")
        .first()
    )


# ---------------------------------------------------------------------------
# Organisation helpers
# ---------------------------------------------------------------------------

def get_user_organization(user):
    if not getattr(user, "is_authenticated", False):
        return None
    from saas.models import Organization, TeamMember

    org = Organization.objects.filter(owner=user).order_by("id").first()
    if org:
        return org
    membership = (
        TeamMember.objects.select_related("org").filter(user=user).order_by("id").first()
    )
    return membership.org if membership else None


def user_can_manage_subscription(user, organization):
    if not getattr(user, "is_authenticated", False) or not organization:
        return False
    return user.is_superuser or organization.owner_id == user.id


def get_subscription_limits(subscription):
    if not subscription:
        return None
    return getattr(subscription, "planlimit", None)


@transaction.atomic
def assign_subscription(organization, subscription):
    organization.subscription = subscription
    organization.save(update_fields=["subscription"])
    return organization


def sync_subscription_permissions():
    permission_map = dict(SUBSCRIPTION_PERMISSIONS)
    for subscription in Subscription.objects.prefetch_related("groups", "permissions"):
        if not subscription.permissions.exists():
            permissions = Permission.objects.filter(
                content_type__app_label="subscriptions",
                codename__in=permission_map.keys(),
            )
            subscription.permissions.set(permissions.filter(codename=subscription.slug))
        for group in subscription.groups.all():
            group.permissions.add(*subscription.permissions.all())


# ---------------------------------------------------------------------------
# Stripe helpers
# ---------------------------------------------------------------------------

def get_or_create_stripe_customer(organization):
    """
    Ensure the organisation has a Stripe Customer ID.
    Prefers the StripeSubscription record, falls back to org.stripe_customer_id.
    """
    # Check StripeSubscription table first
    try:
        stripe_sub = organization.stripe_subscription
        if stripe_sub.stripe_customer_id:
            return stripe_sub.stripe_customer_id
    except StripeSubscription.DoesNotExist:
        pass

    # Fall back to organization model field
    if organization.stripe_customer_id:
        return organization.stripe_customer_id

    # Create a new Stripe Customer
    if not Customer:
        raise Exception("Stripe Customer resource is not available.")

    customer = Customer.create(
        name=organization.name,
        email=organization.owner.email,
        metadata={"organization_id": organization.pk, "owner": organization.owner.email},
    )
    # Persist
    organization.stripe_customer_id = customer.id
    organization.save(update_fields=["stripe_customer_id"])
    return customer.id


def create_stripe_checkout_session(organization, subscription, billing_interval, success_url, cancel_url):
    """
    Create a Stripe Checkout Session for upgrading/subscribing.
    Returns (session_url, error_message). On free plan, returns (None, None).
    """
    if subscription.is_free:
        return None, None  # Free plan — direct DB update, no Stripe

    if not checkout:
        return None, "Stripe Checkout is not available in the current environment."

    price_id = (
        subscription.stripe_annual_price_id
        if billing_interval == "annual"
        else subscription.stripe_monthly_price_id
    )

    if not price_id:
        return None, (
            f"Stripe price ID not configured for {subscription.name} "
            f"({billing_interval}). Please set it in the admin."
        )

    customer_id = get_or_create_stripe_customer(organization)

    session = checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        currency="inr",
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        metadata={
            "organization_id": organization.pk,
            "subscription_id": subscription.pk,
            "billing_interval": billing_interval,
        },
        subscription_data={
            "metadata": {
                "organization_id": organization.pk,
                "subscription_id": subscription.pk,
            }
        },
    )
    return session.url, None


def create_customer_portal_session(organization, return_url):
    """
    Create a Stripe Customer Portal session for managing subscriptions.
    """
    if not billing_portal:
        raise Exception("Stripe Customer Portal is not available in the current environment.")
        
    customer_id = get_or_create_stripe_customer(organization)
    session = billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url
