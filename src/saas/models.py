from django.db import models
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription

User = get_user_model()

COMPANY_SIZE_CHOICES = [
    ("1-10", "1-10"),
    ("11-50", "11-50"),
    ("51-200", "51-200"),
    ("201-500", "201-500"),
    ("500+", "500+"),
]

INDUSTRY_CHOICES = [
    ("tech", "Technology"),
    ("finance", "Finance"),
    ("education", "Education"),
    ("health", "Healthcare"),
    ("other", "Other"),
]

TIME_SLOT_CHOICES = [
    ("morning", "Morning"),
    ("afternoon", "Afternoon"),
    ("evening", "Evening"),
]


# ---------------------------------------------------------------------------
# Role Definitions (RBAC)
# ---------------------------------------------------------------------------

ROLE_OWNER = "owner"     # Full control, including deletion and billing management.
ROLE_ADMIN = "admin"     # Management access (members, apps, buckets).
ROLE_DEVELOPER = "devel" # Technical access (deploy apps, create buckets).
ROLE_VIEWER = "viewer"   # Read-only access.

ROLE_CHOICES = [
    (ROLE_OWNER, "Owner"),
    (ROLE_ADMIN, "Administrator"),
    (ROLE_DEVELOPER, "Developer"),
    (ROLE_VIEWER, "Viewer"),
]


class TrialSignup(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    company_size = models.CharField(
        max_length=20, choices=COMPANY_SIZE_CHOICES, blank=True
    )
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True)
    terms_accepted = models.BooleanField()
    newsletter_opt_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"


class DemoSchedule(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=150)
    job_title = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES)
    preferred_date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES)
    use_case = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demo for {self.first_name} {self.last_name} on {self.preferred_date} at {self.time_slot}"


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolve = models.BooleanField(default=False)
    email_history = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.first_name} {self.last_name}: {self.subject}"


class Feature(models.Model):
    icon = models.CharField(
        max_length=100, help_text="Heroicons SVG path or custom icon class"
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    color = models.CharField(
        max_length=50,
        default="indigo",
        help_text="Tailwind color name, e.g., indigo, pink, blue",
    )

    active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.title


class Organization(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Infrastructure Governance
    storage_limit_mb = models.IntegerField(default=1024) # 1GB Default
    deployment_root = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("manage_members", "Can manage organization team members"),
            ("manage_billing", "Can manage organization subscription and billing"),
            ("destroy_organization", "Can delete the organization (Owner Only)"),
        ]

    def get_total_usage_mb(self):
        # 1. Bucket Object Storage
        bucket_usage = 0
        for bucket in self.buckets.all():
            bucket_usage += bucket.usage_mb
            
        # 2. Compute App Artifacts
        app_usage_bytes = 0
        for app in self.apps.all():
            for dep in app.deployments.all():
                if dep.artifact:
                    try:
                        app_usage_bytes += dep.artifact.size
                    except Exception:
                        pass
            
        app_usage_mb = app_usage_bytes / (1024 * 1024)
        
        return round(bucket_usage + app_usage_mb, 2)


class Usage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    api_calls = models.IntegerField(default=0)
    storage_mb = models.FloatField(default=0)
    active_users = models.IntegerField(default=1)

    automations_run = models.IntegerField(default=0)
    reports_generated = models.IntegerField(default=0)

    revenue = models.FloatField(default=0)

    updated_at = models.DateTimeField(auto_now=True)


class Event(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)


class OrganizationRole(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_preset = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('org', 'name')

    def __str__(self):
        return f"{self.name} ({self.org.name})"

class RolePermission(models.Model):
    role = models.ForeignKey(OrganizationRole, on_delete=models.CASCADE, related_name='permissions')
    permission_codename = models.CharField(max_length=255) # e.g. 'buckets.add_app'

    class Meta:
        unique_together = ('role', 'permission_codename')

    def __str__(self):
        return f"{self.role.name} -> {self.permission_codename}"

class TeamMember(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=ROLE_DEVELOPER)
    # New Dynamic Role link
    role_obj = models.ForeignKey(OrganizationRole, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("org", "user")

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()} in {self.org.name}"


class Automation(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    trigger = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)


class UsageEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    value = models.FloatField(default=0)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
