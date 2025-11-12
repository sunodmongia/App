from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["profile_image", "phone", "bio"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add consistent placeholders and Tailwind classes
        self.fields["phone"].widget.attrs.update(
            {
                "placeholder": "Enter your phone number",
            }
        )
        self.fields["bio"].widget.attrs.update(
            {"placeholder": "Write something about yourself...", "rows": 4}
        )
