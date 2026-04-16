from django.contrib import admin
from .models import PlanLimit, Subscription, StripeSubscription


class PlanLimitInline(admin.StackedInline):
    model = PlanLimit
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "name", "slug", "monthly_price", "annual_price",
        "active", "is_default", "is_featured",
        "stripe_monthly_price_id", "stripe_annual_price_id",
    )
    list_filter = ("active", "is_default", "is_featured")
    search_fields = ("name", "slug", "description")
    readonly_fields = ("currency",)
    fieldsets = (
        ("Plan", {
            "fields": ("name", "slug", "description", "features", "display_order",
                       "active", "is_default", "is_featured"),
        }),
        ("Pricing (INR ₹)", {
            "fields": ("monthly_price", "annual_price", "currency"),
        }),
        ("Stripe", {
            "fields": ("stripe_monthly_price_id", "stripe_annual_price_id"),
            "description": (
                "Enter Stripe Price IDs from your Stripe Dashboard. "
                "Create Products → Prices for monthly & annual at "
                "the amounts above, then paste the price_xxxxx IDs here."
            ),
        }),
        ("Permissions & Groups", {
            "fields": ("permissions", "groups"),
            "classes": ("collapse",),
        }),
    )
    inlines = [PlanLimitInline]


@admin.register(PlanLimit)
class PlanLimitAdmin(admin.ModelAdmin):
    list_display = ("subscription", "api_calls", "storage_display", "automations", "team_members")

    @admin.display(description="Storage")
    def storage_display(self, obj):
        return obj.storage_display


@admin.register(StripeSubscription)
class StripeSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "organization", "subscription", "billing_interval",
        "status", "current_period_end", "updated_at",
    )
    list_filter = ("status", "billing_interval")
    search_fields = ("organization__name", "stripe_subscription_id", "stripe_customer_id")
    readonly_fields = ("created_at", "updated_at")
