from django.contrib import admin
from saas.models import *
from django.core.mail import send_mail
from django.contrib import messages


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
    list_display = ("first_name", "last_name", "email", "subject")
    search_fields = ("first_name", "last_name", "email", "subject")
    readonly_fields = ["first_name", "last_name", "email", "subject", "message"]
    actions = ["mark_as_resolved"]
    

    @admin.action(description="Mark the problem as resolved and Send Email")
    def mark_as_resolved(self, request, queryset):
        for obj in queryset:
            if not obj.resolved:
                obj.resolved = True
                obj.save()
        send_mail(
            subject=f"Your query has been resolved: {obj.subject}",
            message=(
                f"Dear {obj.first_name},\n\n"
                f"Your message has been reviewed and marked as resolved.\n\n"
                f"Message:\n{obj.message}\n\n"
                f"Thank you for contacting us."
            ),
            from_email="sunodmongia2003@gmail.com",
            recipient_list=[obj.email],
            fail_silently=True,
        )

        self.message_user(
            request,
            f"{queryset.count()} message(s) marked as resolved and emails sent.",
            level=messages.SUCCESS,
        )
