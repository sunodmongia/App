# forms.py

from django import forms
from .models import TrialSignup, DemoSchedule


class TrialSignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Create a strong password"}),
        help_text="Minimum 8 characters with letters and numbers",
    )

    class Meta:
        model = TrialSignup
        fields = [
            "first_name",
            "last_name",
            "email",
            "company",
            "password",
            "company_size",
            "industry",
            "terms_accepted",
            "newsletter_opt_in",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your First name",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Enter your Last name",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter your email address",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "placeholder": "Enter your company name",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "company_size": forms.Select(
                attrs={
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                }
            ),
            "industry": forms.Select(
                attrs={
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                }
            ),
            "terms_accepted": forms.CheckboxInput(
                attrs={
                    "class": "mt-1 mr-3 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                }
            ),
            "newsletter_opt_in": forms.CheckboxInput(
                attrs={
                    "class": "mt-1 mr-3 h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                }
            ),
        }


class DemoScheduleCallForm(forms.ModelForm):
    class Meta:
        model = DemoSchedule
        fields = "__all__"
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "John",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Doe",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "john@company.com",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "+1 (555) 123-4567",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "placeholder": "Your Company Inc.",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "job_title": forms.TextInput(
                attrs={
                    "placeholder": "CEO, Marketing Manager, etc.",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "company_size": forms.Select(
                attrs={
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                }
            ),
            "preferred_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "time_slot": forms.Select(
                attrs={
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                }
            ),
            "use_case": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us about your specific use case…",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none resize-none",
                }
            ),
        }
