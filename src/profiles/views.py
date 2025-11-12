from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, UpdateView, ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from .forms import UserProfileForm

User = get_user_model()


# ---------------------------------------------------------------------
# ADMIN — Profile List (Paginated, Searchable)
# ---------------------------------------------------------------------
class ProfileListView(UserPassesTestMixin, ListView):
    model = UserProfile
    template_name = "profiles/list.html"
    context_object_name = "profiles"
    paginate_by = 10
    ordering = ["user__username"]

    def test_func(self):
        """Only staff/admin users can access this view."""
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect("profile-home")

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(user__username__icontains=query)
        return queryset


# ---------------------------------------------------------------------
# USER — My Profile (current logged-in user)
# ---------------------------------------------------------------------
class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/profiles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Safely ensure profile exists
        profile, _ = UserProfile.objects.get_or_create(user=user)

        context.update(
            {
                "user": user,
                "profile": profile,
                "recent_activities": (
                    getattr(profile, "activities", []).all().order_by("-timestamp")[:5]
                    if hasattr(profile, "activities")
                    else []
                ),
            }
        )
        return context


# ---------------------------------------------------------------------
# USER — Edit Profile
# ---------------------------------------------------------------------
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "profiles/edit_profile.html"

    def get_object(self, queryset=None):
        # Ensure a profile exists even if user never edited before
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        form.save()
        return redirect("profile-home")


# ---------------------------------------------------------------------
# PUBLIC — View Another User’s Profile
# ---------------------------------------------------------------------
class UserProfileView(DetailView):
    model = User
    template_name = "profiles/user_profile.html"  
    context_object_name = "profile_user"

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get("username"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = self.get_object()

        # Always ensure profile exists
        profile, _ = UserProfile.objects.get_or_create(user=user_obj)

        context.update(
            {
                "profile": profile,
                "is_me": self.request.user.is_authenticated
                and self.request.user == user_obj,
            }
        )
        return context
