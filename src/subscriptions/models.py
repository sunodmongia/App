from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import Group, Permission


SUBSCRIPTION_PERMISSIONS = [
    ("starter", "starter perm"),
    ("professional", "professional perm"),
    ("enterprise", "enterprise perm"),
]


class Subscription(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # INR only
    currency = models.CharField(max_length=10, default="INR", editable=False)
    is_default = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    features = models.JSONField(default=list, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    active = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        limit_choices_to={
            "content_type__app_label": "subscriptions",
            "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS],
        },
    )
    # Stripe Price IDs (fill via admin after creating products in Stripe dashboard)
    stripe_monthly_price_id = models.CharField(
        max_length=100, blank=True,
        help_text="Stripe Price ID for monthly billing (e.g. price_xxxxx)"
    )
    stripe_annual_price_id = models.CharField(
        max_length=100, blank=True,
        help_text="Stripe Price ID for annual billing (e.g. price_xxxxx)"
    )

    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
        ordering = ["display_order", "monthly_price", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.currency = "INR"  # Always INR
        super().save(*args, **kwargs)

    @property
    def is_free(self):
        return self.monthly_price == 0

    @property
    def currency_symbol(self):
        return "₹"

    @property
    def billing_currency_symbol(self):
        return "₹"


class PlanLimit(models.Model):
    subscription = models.OneToOneField(
        Subscription, on_delete=models.CASCADE, related_name="planlimit"
    )
    api_calls = models.IntegerField(default=0)
    storage_mb = models.IntegerField(default=0)
    automations = models.IntegerField(default=0)
    team_members = models.IntegerField(default=1)

    @property
    def storage_display(self):
        mb = self.storage_mb
        if mb == 0:
            return "0 MB"
        if mb >= 1024 * 1024:
            return f"{mb // (1024 * 1024)} TB"
        if mb >= 1024:
            if mb % 1024 == 0:
                return f"{mb // 1024} GB"
            return f"{mb / 1024:.1f} GB"
        return f"{mb} MB"

    @property
    def api_calls_display(self):
        if self.api_calls >= 1_000_000:
            return f"{self.api_calls // 1_000_000}M"
        if self.api_calls >= 1_000:
            return f"{self.api_calls // 1_000}K"
        return str(self.api_calls)

    def __str__(self):
        return f"{self.subscription.name} limits"


class StripeSubscription(models.Model):
    """Tracks an active Stripe subscription for an Organization."""
    STATUS_CHOICES = [
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
        ("incomplete", "Incomplete"),
        ("trialing", "Trialing"),
    ]

    organization = models.OneToOneField(
        "saas.Organization",
        on_delete=models.CASCADE,
        related_name="stripe_subscription",
    )
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True
    )
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    billing_interval = models.CharField(
        max_length=10, choices=[("monthly", "Monthly"), ("annual", "Annual")],
        default="monthly"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="incomplete")
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.organization.name} — {self.subscription}"
