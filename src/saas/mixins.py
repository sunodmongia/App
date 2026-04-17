from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from saas.permissions import has_org_permission
from subscriptions.services import get_user_organization

class TenantPermissionMixin(LoginRequiredMixin):
    """
    Enforces RBAC permissions at the tenant level.
    Usage:
        class MyView(TenantPermissionMixin, View):
            permission_required = 'buckets.manage_apps'
    """
    permission_required = None
    redirect_url = 'dashboard'

    def get_organization(self):
        """Standard hook to resolve the current organization."""
        # This defaults to the user's primary/active org. 
        # For DetailViews, we would override this to get the org from the object.
        return get_user_organization(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        # 1. Login check (from LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # 2. Resolve organization
        self.org = self.get_organization()
        if not self.org:
            messages.error(request, "Organization context required for this action.")
            return redirect(self.redirect_url)

        # 3. Resolve permissions (RBAC)
        if self.permission_required:
            if not has_org_permission(request.user, self.org, self.permission_required):
                messages.error(request, f"Access Denied: You do not have permission to perform this action ({self.permission_required}).")
                return redirect(self.redirect_url)

        return super().dispatch(request, *args, **kwargs)
