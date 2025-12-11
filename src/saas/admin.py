from django.contrib import admin
from saas.models import *
from django.core.mail import send_mail
from django.contrib import messages
from .forms import *
from django.utils import timezone

# importing request
from django.http import request


@admin.register(TrialSignup)
class TrialSignupAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "company", "created_at")
    list_filter = ("company_size", "industry", "created_at")
    search_fields = ("first_name", "last_name", "email", "created_at")


@admin.register(DemoSchedule)
class DemoScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "company",
        "time_slot",
        "preferred_date",
        "created_at",
    )
    list_filter = ("company_size", "preferred_date", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "company")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    form = ContactMessageAdminForm

    change_form_template = "change_form.html"

    change_form_template = "change_form.html"

    list_display = (
        "first_name",
        "last_name",
        "email",
        "subject",
        "resolve",
        "created_at",
    )
    list_filter = ("resolve", "created_at")
    search_fields = ("first_name", "last_name", "email", "subject")
    readonly_fields = (
        "first_name",
        "last_name",
        "email",
        "subject",
        "message",
        "created_at",
    )

    fields = [
        "first_name",
        "last_name",
        "email",
        "subject",
        "message",
        "resolve",
        "created_at",
        "custom_email_subject",
        "custom_email_message",
    ]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)

        if request.method == "POST" and "send_custom_email" in request.POST:
            form = self.get_form(request, obj)(request.POST, instance=obj)
            if form.is_valid():
                subject = form.cleaned_data.get("custom_email_subject")
                message = form.cleaned_data.get("custom_email_message")

                if subject and message:
                    try:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email="sunodmongia2003@gmail.com",
                            recipient_list=[obj.email],
                            fail_silently=False,
                        )

                        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
                        history_entry = (
                            f"[{timestamp}] Subject: {subject}\n{message}\n\n"
                        )
                        obj.email_history += history_entry
                        obj.save(update_fields=["email_history"])

                        self.message_user(
                            request,
                            f"✅ Email sent successfully to {obj.email}",
                            level=messages.SUCCESS,
                        )
                    except Exception as e:
                        self.message_user(
                            request,
                            f"❌ Failed to send email: {str(e)}",
                            level=messages.ERROR,
                        )
            return super().response_change(request, obj)

        return super().change_view(request, object_id, form_url, extra_context)

    fields = [
        "first_name",
        "last_name",
        "email",
        "subject",
        "message",
        "resolve",
        "created_at",
        "custom_email_subject",
        "custom_email_message",
    ]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)

        if request.method == "POST" and "send_custom_email" in request.POST:
            form = self.get_form(request, obj)(request.POST, instance=obj)
            if form.is_valid():
                subject = form.cleaned_data.get("custom_email_subject")
                message = form.cleaned_data.get("custom_email_message")

                if subject and message:
                    try:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email="sunodmongia2003@gmail.com",
                            recipient_list=[obj.email],
                            fail_silently=False,
                        )

                        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
                        history_entry = (
                            f"[{timestamp}] Subject: {subject}\n{message}\n\n"
                        )
                        obj.email_history += history_entry
                        obj.save(update_fields=["email_history"])

                        self.message_user(
                            request,
                            f"✅ Email sent successfully to {obj.email}",
                            level=messages.SUCCESS,
                        )
                    except Exception as e:
                        self.message_user(
                            request,
                            f"❌ Failed to send email: {str(e)}",
                            level=messages.ERROR,
                        )
            return super().response_change(request, obj)

        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "display_order")
    list_editable = ("active", "display_order")
    search_fields = ("title",)
