from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
import os
from .models import *
from .forms import *

User = get_user_model()


class UserProfileDetailView(DetailView):
    model = UserProfile
    template_name = "profiles/profile_detail.html"
    context_object_name = "profile"

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
class ProfileEditView(LoginRequiredMixin, View):
    template_name = "profiles/edit_profile.html"

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = user.userprofile
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "user_obj": user,
            },
        )

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = user.userprofile

        if "remove_image" in request.POST:
            if profile.profile_image and os.path.isfile(profile.profile_image.path):
                os.remove(profile.profile_image.path)
                profile.profile_image = None
                profile.save()
            return redirect("profile-edit", pk=pk)

        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("profile-list")

        return render(
            request,
            self.template_name,
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "user_obj": user,
            },
        )


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

# ---------------------------------------------------------------------
# PUBLIC — Delete Profile 
# ---------------------------------------------------------------------

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = UserProfile
    template_name = "profiles/profile_confirm_delete.html"
    success_url = reverse_lazy("profile-list")

    def get_object(self, queryset=None):
        profile = super().get_object(queryset)
        if profile.profile_image and os.path.isfile(profile.profile_image.path):
            os.remove(profile.profile_image.path)
        return profile
