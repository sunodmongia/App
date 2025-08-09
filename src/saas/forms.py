from django import forms
from .models import TrialSignup, DemoSchedule, ContactMessage


class TrialSignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Create a strong password"}),
        help_text="Minimum 8 characters with letters and numbers",
    )

    class Meta:
        model = TrialSignup
        fields = "__all__"
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
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "+1 (555) 123-4567",
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
                    "class": "h-4 w-4 text-black border border-black focus:ring-purple-500 rounded"
                }
            ),
            "newsletter_opt_in": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-black border border-black focus:ring-purple-500 rounded"
                }
            ),
        }
        labels = {
            "terms_accepted": "I accept the terms and conditions",
            "newsletter_opt_in": "Subscribe to our newsletter",
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


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = "__all__"
        exclude = ["created_at"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your name",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "you@example.com",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "placeholder": "Subject",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Your message...",
                    "class": "form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none resize-none",
                }
            ),
        }
