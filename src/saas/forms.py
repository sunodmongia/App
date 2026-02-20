from django import forms
from .models import TrialSignup, DemoSchedule, ContactMessage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div


# ------------------------
# Shared Tailwind styles
# ------------------------
BASE_INPUT = (
    "w-full px-4 py-3 rounded-lg bg-slate-900 text-slate-200 border border-white/10 "
    "focus:outline-none focus:ring-2 focus:ring-indigo-500 "
    "focus:border-indigo-500 transition-colors"
)
CHECKBOX = "h-4 w-4 text-indigo-600 bg-slate-900 border-white/20 rounded focus:ring-indigo-500"
TEXTAREA = f"{BASE_INPUT} resize-none"


# ------------------------
# Trial Signup Form
# ------------------------
class TrialSignupForm(forms.ModelForm):
    class Meta:
        model = TrialSignup
        fields = "__all__"
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "Enter your First name", "class": BASE_INPUT}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Enter your Last name", "class": BASE_INPUT}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Enter your email address", "class": BASE_INPUT}
            ),
            "company": forms.TextInput(
                attrs={"placeholder": "Enter your company name", "class": BASE_INPUT}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "+1 (555) 123-4567", "class": BASE_INPUT}
            ),
            "company_size": forms.Select(attrs={"class": BASE_INPUT}),
            "industry": forms.Select(attrs={"class": BASE_INPUT}),
            "terms_accepted": forms.CheckboxInput(attrs={"class": CHECKBOX}),
            "newsletter_opt_in": forms.CheckboxInput(attrs={"class": CHECKBOX}),
        }
        labels = {
            "terms_accepted": "I accept the terms and conditions",
            "newsletter_opt_in": "Subscribe to our newsletter",
        }


# ------------------------
# Demo Schedule Call Form
# ------------------------
class DemoScheduleCallForm(forms.ModelForm):
    class Meta:
        model = DemoSchedule
        fields = "__all__"
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "John", "class": BASE_INPUT}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Doe", "class": BASE_INPUT}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "john@company.com", "class": BASE_INPUT}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "+1 (555) 123-4567", "class": BASE_INPUT}
            ),
            "company": forms.TextInput(
                attrs={"placeholder": "Your Company Inc.", "class": BASE_INPUT}
            ),
            "job_title": forms.TextInput(
                attrs={
                    "placeholder": "CEO, Marketing Manager, etc.",
                    "class": BASE_INPUT,
                }
            ),
            "company_size": forms.Select(attrs={"class": BASE_INPUT}),
            "preferred_date": forms.DateInput(
                attrs={"type": "date", "class": BASE_INPUT}
            ),
            "time_slot": forms.Select(attrs={"class": BASE_INPUT}),
            "use_case": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us about your specific use case…",
                    "class": TEXTAREA,
                }
            ),
        }


# ------------------------
# Contact Form
# ------------------------
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = "__all__"
        exclude = [ "resolve", "email_history", "created_at"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Your name", "class": BASE_INPUT}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "you@example.com", "class": BASE_INPUT}
            ),
            "subject": forms.TextInput(
                attrs={"placeholder": "Subject", "class": BASE_INPUT}
            ),
            "message": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Your message...", "class": TEXTAREA}
            ),
        }


# ------------------------
# Admin Reply Form
# ------------------------
class ContactMessageAdminForm(forms.ModelForm):
    custom_email_subject = forms.CharField(
        required=False,
        label="Custom Email Subject",
        widget=forms.TextInput(attrs={"class": "vTextField w-full", "size": "80"}),
    )

    custom_email_message = forms.CharField(
        required=False,
        label="Custom Email Message",
        widget=forms.Textarea(
            attrs={"class": "vLargeTextField w-full", "rows": 8, "cols": 80}
        ),
    )

    class Meta:
        model = ContactMessage
        fields = "__all__"
