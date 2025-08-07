from allauth.account.signals import user_logged_in, password_changed
from allauth.socialaccount.signals import pre_social_login
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


@receiver(user_logged_in)
def on_user_logged_in(request, user, **kwargs):
    # Email content
    subject = "Login Notification"
    message = render_to_string(
        "emails/login_notification.txt",
        {
            "user": user,
            "ip": get_client_ip(request),
        },
    )
    html_message = render_to_string(
        "emails/login_notification.html",
        {
            "user": user,
            "ip": get_client_ip(request),
        },
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


@receiver(password_changed)
def on_password_change(request, user, **kwargs):
    subject = "Your Password Was Changed"
    message = render_to_string(
        "emails/password_changed.txt",
        {
            "user": user,
        },
    )
    html_message = render_to_string(
        "emails/password_changed.html",
        {
            "user": user,
        },
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


@receiver(pre_social_login)
def on_pre_social_login(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    provider = sociallogin.account.provider
    subject = "Social Login Attempt"
    message = render_to_string(
        "emails/social_login_attempt.txt",
        {
            "user": user,
            "provider": provider,
        },
    )
    html_message = render_to_string(
        "emails/social_login_attempt.html",
        {
            "user": user,
            "provider": provider,
        },
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=True,
    )


def get_client_ip(request):
    """Helper to retrieve client IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
