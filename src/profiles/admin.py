from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"

# Extend the existing User admin
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # Optional: show extra fields directly in the list view
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_select_related = ("userprofile",)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register separately (if you want to access UserProfile directly too)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "phone")
