from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings


from saas.forms import *
from saas.models import *


class HomeView(TemplateView):
    template_name = "home.html"


class AboutView(TemplateView):
    template_name = "about.html"


class UserDemoView(LoginRequiredMixin, TemplateView):
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
        # Hash and save password
        instance = form.save(commit=False)
        raw_password = form.cleaned_data["password"]
        instance.password_hash = make_password(raw_password)
        instance.save()
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

        # Send email to user
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


class PricingView(TemplateView):
    template_name = "pricing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Pricing"
        return context


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


class APIView(TemplateView):
    template_name = "api.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "API"
        return context


class FeaturesView(TemplateView):
    template_name = "features.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Features"
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



class FeaturesView(TemplateView):
    template_name = "features.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["features"] = Feature.objects.filter(active=True)
        return context
    

