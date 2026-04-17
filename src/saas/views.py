from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView, View
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse_lazy
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum, Count, Q, Max, FloatField
from django.db.models.functions import Cast, TruncDate, TruncHour
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .mixins import TenantPermissionMixin

from .models import (
    Organization, Event, Usage, Automation, Feature,
)
from buckets.models import Bucket, App  # Added for infrastructure tracking
from .forms import TrialSignupForm, DemoScheduleCallForm, ContactForm
from saas.events import log_event
from subscriptions.services import (
    get_active_subscriptions,
    ensure_default_subscriptions,
    get_default_subscription,
    get_user_organization,
    user_can_manage_subscription,
)


class HomeView(TemplateView):
    template_name = "home.html"


class AboutView(TemplateView):
    template_name = "about.html"


class BlogView(TemplateView):
    template_name = "blog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Blogs"
        return context


class CaseStudyView(TemplateView):
    template_name = "case_study.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Case Study"
        return context


class FeaturesView(TemplateView):
    template_name = "features.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Features"
        context["features"] = Feature.objects.filter(active=True)
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Privacy Policy"
        return context


class TermsAndConditionsView(TemplateView):
    template_name = "terms_and_condition.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Terms and Conditions"
        return context


class SaasAPIView(TemplateView):
    template_name = "api.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "API"
        return context


class UserDemoView(TemplateView):
    template_name = "demo.html"
    login_url = "account_login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Demo"
        return context


class StartTrialView(LoginRequiredMixin, FormView):
    template_name = "signup_trial.html"
    form_class = TrialSignupForm
    success_url = reverse_lazy("pricing")

    def form_valid(self, form):
        instance = form.save()
        messages.success(self.request, "Your free trial signup has been saved.")
        send_mail(
            subject="Your Free Trial Has Started",
            message=(
                f"Hello {instance.first_name} {instance.last_name},\n\n"
                "Thank you for signing up for our free trial. "
                "You can now enjoy all premium features for the trial period.\n\n"
                "Best Regards,\nThe Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Start Trial"
        return context


class ScheduleDemoView(LoginRequiredMixin, FormView):
    template_name = "schedule_demo.html"
    form_class = DemoScheduleCallForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        instance = form.save()
        send_mail(
            subject="Your Demo Has Been Scheduled",
            message=(
                f"Hello {instance.first_name} {instance.last_name},\n\n"
                "Thank you for scheduling a demo with us. "
                "We will contact you soon to confirm the details.\n\n"
                "Best Regards,\nThe Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )
        messages.success(
            self.request,
            "Your demo scheduling request has been saved and a confirmation email has been sent.",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Schedule a Demo"
        return context


class ContactUsView(LoginRequiredMixin, FormView):
    template_name = "contact_us.html"
    form_class = ContactForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks for Contacting Us")
        return super().form_valid(form)


class PricingView(TenantPermissionMixin, TemplateView):
    permission_required = 'saas.view_billing'
    template_name = "pricing.html"

    def get_context_data(self, **kwargs):
        from subscriptions.models import StripeSubscription
        context = super().get_context_data(**kwargs)
        context["title"] = "Pricing"
        context["plans"] = get_active_subscriptions()
        
        # Fallback: if no plans exist, attempt one-time bootstrap
        if not context["plans"].exists():
            context["plans"] = ensure_default_subscriptions()

        context["organization"] = get_user_organization(self.request.user)
        context["current_subscription"] = None
        context["has_stripe_subscription"] = False
        context["stripe_publishable_key"] = settings.STRIPE_PUBLISHABLE_KEY

        if context["organization"]:
            context["current_subscription"] = context["organization"].subscription
            try:
                ss = context["organization"].stripe_subscription
                context["has_stripe_subscription"] = ss.status in ("active", "trialing", "past_due")
            except StripeSubscription.DoesNotExist:
                pass

        context["default_subscription"] = get_default_subscription()
        context["can_manage_subscription"] = user_can_manage_subscription(
            self.request.user, context["organization"]
        )
# --- RBAC Management Views ---

def seed_default_roles(org):
    """Auto-provisions standard roles for an organization."""
    from saas.permissions import ROLE_PERMISSION_MAP
    from saas.models import OrganizationRole, RolePermission

    for role_name, perms in ROLE_PERMISSION_MAP.items():
        role_obj, created = OrganizationRole.objects.get_or_create(
            org=org, 
            name=role_name.capitalize(),
            defaults={'is_preset': True}
        )
        if created:
            for p_code in perms:
                RolePermission.objects.get_or_create(role=role_obj, permission_codename=p_code)

class RoleManagementView(TenantPermissionMixin, TemplateView):
    permission_required = 'saas.manage_members'
    template_name = "saas/roles_manage.html"

    def get_context_data(self, **kwargs):
        from saas.models import OrganizationRole
        from saas.permissions import MANAGEMENT_PERMISSIONS
        context = super().get_context_data(**kwargs)
        
        # Ensure default roles exist
        if not OrganizationRole.objects.filter(org=self.org).exists():
            seed_default_roles(self.org)
            
        context['roles'] = OrganizationRole.objects.filter(org=self.org).order_by('is_preset', 'created_at')
        context['available_permissions'] = MANAGEMENT_PERMISSIONS
        return context

    def post(self, request, *args, **kwargs):
        from saas.models import OrganizationRole
        name = request.POST.get('name', '').strip()
        if name:
            OrganizationRole.objects.create(org=self.org, name=name)
            messages.success(request, f"Custom role '{name}' created.")
        return redirect('saas:role_manage')

class RolePermissionUpdateView(TenantPermissionMixin, View):
    permission_required = 'saas.manage_members'

    def post(self, request, role_id):
        from saas.models import OrganizationRole, RolePermission
        role_obj = get_object_or_404(OrganizationRole, id=role_id, org=self.org)
        permission_codename = request.POST.get('permission')
        action = request.POST.get('action') # 'add' or 'remove'

        if action == 'add':
            RolePermission.objects.get_or_create(role=role_obj, permission_codename=permission_codename)
        else:
            RolePermission.objects.filter(role=role_obj, permission_codename=permission_codename).delete()

        return JsonResponse({'status': 'success'})

class MemberManagementView(TenantPermissionMixin, TemplateView):
    permission_required = 'saas.manage_members'
    template_name = "saas/member_manage.html"

    def get_context_data(self, **kwargs):
        from saas.models import TeamMember, OrganizationRole
        context = super().get_context_data(**kwargs)
        context['members'] = TeamMember.objects.filter(org=self.org).select_related('user', 'role_obj')
        context['roles'] = OrganizationRole.objects.filter(org=self.org)
        return context

    def post(self, request, member_id=None):
        from saas.models import TeamMember, OrganizationRole
        from django.contrib.auth import get_user_model
        User = get_user_model()

        role_id = request.POST.get('role_id')
        
        # 1. Update Existing Member
        if member_id:
            member = get_object_or_404(TeamMember, id=member_id, org=self.org)
            if role_id:
                role_obj = get_object_or_404(OrganizationRole, id=role_id, org=self.org)
                member.role_obj = role_obj
                member.save()
                messages.success(request, f"Authority for {member.user.username} synced to {role_obj.name}.")
            return redirect('saas:member_manage')

        # 2. Add New Member by Username
        username = request.POST.get('username')
        if username and role_id:
            try:
                user_to_add = User.objects.get(username=username)
                role_to_assign = get_object_or_404(OrganizationRole, id=role_id, org=self.org)
                
                # Check for existing membership
                if TeamMember.objects.filter(org=self.org, user=user_to_add).exists():
                    messages.warning(request, f"{username} is already an active member of this organization.")
                else:
                    TeamMember.objects.create(org=self.org, user=user_to_add, role_obj=role_to_assign)
                    messages.success(request, f"Access provisioned: {username} added as {role_to_assign.name}.")
            except User.DoesNotExist:
                messages.error(request, f"Identity verification failed: User '{username}' not found on the platform.")
        
        return redirect('saas:member_manage')

class CustomerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        result = f"processed {prompt}"
        return Response({"result": result})


class DashboardView(TenantPermissionMixin, TemplateView):
    permission_required = 'buckets.view_apps'
    template_name = "dashboard.html"

    def _get_days(self):
        try:
            return max(1, min(int(self.request.GET.get("days", 30)), 365))
        except (TypeError, ValueError):
            return 30

    def _get_orgs(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Organization.objects.all()
        # Return orgs where user is owner OR a team member
        from saas.models import TeamMember
        return Organization.objects.filter(
            Q(owner=user) | Q(teammember__user=user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = self._get_days()
        start_date = now() - timedelta(days=days)
        orgs = self._get_orgs()

        context["active_orgs"] = orgs.filter(event__created_at__gte=start_date).distinct().count()
        context["total_orgs"] = orgs.count()

        context["total_revenue"] = Event.objects.filter(
            org__in=orgs, type="revenue", created_at__gte=start_date
        ).aggregate(total=Sum(Cast("data__amount", FloatField())))["total"] or 0

        context["total_api"] = Event.objects.filter(
            org__in=orgs, type="api_call", created_at__gte=start_date
        ).count()

        context["total_automations"] = Automation.objects.filter(org__in=orgs, enabled=True).count()

        context["total_reports"] = Event.objects.filter(
            org__in=orgs, type="report_generated", created_at__gte=start_date
        ).count()

        context["total_active_storage"] = Usage.objects.filter(
            user__in=orgs.values_list("owner_id", flat=True)
        ).aggregate(total=Sum("storage_mb"))["total"] or 0
        
        context["total_reserved_storage"] = Bucket.objects.filter(
            organization__in=orgs
        ).aggregate(total=Sum("quota_mb"))["total"] or 0
        
        context["total_reserved_storage_gb"] = round(context["total_reserved_storage"] / 1024, 1)
        
        context["total_live_deployments"] = App.objects.filter(
            organization__in=orgs, is_live=True
        ).count()

        context["active_apps"] = App.objects.filter(organization__in=orgs, is_live=True).order_by('-last_deployed_at')
        context["deployment_root"] = orgs.first().deployment_root if orgs.exists() else "NOT_CONFIGURED"

        context["compute_fleet"] = list(
            App.objects.filter(organization__in=orgs, is_live=True)
            .values("runtime")
            .annotate(count=Count("id"))
        )

        # Latest events for the live feed
        context["events"] = (
            Event.objects.filter(org__in=orgs, created_at__gte=start_date)
            .order_by("-created_at")[:15]
        )
        
        # Aggregate counts for the distribution chart
        context["event_counts"] = list(
            Event.objects.filter(org__in=orgs, created_at__gte=start_date)
            .values("type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        context["top_orgs"] = orgs.annotate(
            revenue=Sum(
                Cast("event__data__amount", FloatField()),
                filter=Q(event__type="revenue", event__created_at__gte=start_date),
            ),
            api_calls=Count("event", filter=Q(event__type="api_call", event__created_at__gte=start_date)),
            team_size=Count("teammember"),
            automations=Count("automation", filter=Q(automation__enabled=True)),
        ).order_by("-revenue")[:10]

        context["automation_stats"] = (
            orgs.annotate(
                total=Count("automation"),
                enabled=Count("automation", filter=Q(automation__enabled=True)),
            )
            .filter(total__gt=0)
            .order_by("-total")[:10]
        )

        inactive_threshold = now() - timedelta(days=7)
        context["inactive_orgs"] = orgs.annotate(
            last_event=Max("event__created_at")
        ).filter(Q(last_event__lt=inactive_threshold) | Q(last_event__isnull=True))[:10]

        prev_start = start_date - timedelta(days=days)
        prev_revenue = (
            Event.objects.filter(
                org__in=orgs, type="revenue",
                created_at__gte=prev_start, created_at__lt=start_date,
            ).aggregate(total=Sum(Cast("data__amount", FloatField())))["total"] or 0
        )
        context["revenue_growth"] = self._calc_growth(prev_revenue, context["total_revenue"])

        prev_api = Event.objects.filter(
            org__in=orgs, type="api_call",
            created_at__gte=prev_start, created_at__lt=start_date,
        ).count()
        context["api_growth"] = self._calc_growth(prev_api, context["total_api"])

        context["revenue_trends"] = list(
            Event.objects.filter(org__in=orgs, type="revenue", created_at__gte=start_date)
            .annotate(date=TruncHour("created_at"))
            .values("date")
            .annotate(amount=Sum(Cast("data__amount", FloatField())))
            .order_by("date")
        )
        context["api_trends"] = list(
            Event.objects.filter(org__in=orgs, type="api_call", created_at__gte=start_date)
            .annotate(date=TruncHour("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        context["days"] = days
        return context

    def _calc_growth(self, old_value, new_value):
        if old_value == 0:
            return 100 if new_value > 0 else 0
        return round(((new_value - old_value) / old_value) * 100, 1)


def some_api_view(request):
    org = get_user_organization(request.user)
    if not org:
        return JsonResponse({"ok": False, "error": "Organization not found"}, status=404)
    log_event(org, "api_call")
    return JsonResponse({"ok": True})
