from django import forms

from subscriptions.models import Subscription


class SubscriptionChangeForm(forms.Form):
    subscription = forms.ModelChoiceField(
        queryset=Subscription.objects.filter(active=True).order_by("display_order", "name"),
        empty_label=None,
        widget=forms.HiddenInput,
    )
