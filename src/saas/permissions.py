from saas.models import TeamMember, ROLE_OWNER, ROLE_ADMIN, ROLE_DEVELOPER, ROLE_VIEWER

# ---------------------------------------------------------------------------
# Master Role-to-Permission Registry
# ---------------------------------------------------------------------------
# View and logic code should NEVER check for role strings like 'admin'.
# Instead, they should check if the user has a specific permission.

ROLE_PERMISSION_MAP = {
    ROLE_OWNER: [
        "saas.manage_members",
        "saas.view_billing",
        "saas.manage_billing",
        "saas.destroy_organization",
        "buckets.view_storage",
        "buckets.manage_buckets",
        "buckets.upload_files",
        "buckets.view_apps",
        "buckets.manage_apps",
        "buckets.deploy_apps",
        "buckets.control_apps",
    ],
    ROLE_ADMIN: [
        "saas.manage_members",
        "saas.view_billing",
        "saas.manage_billing",
        "buckets.view_storage",
        "buckets.manage_buckets",
        "buckets.upload_files",
        "buckets.view_apps",
        "buckets.manage_apps",
        "buckets.deploy_apps",
        "buckets.control_apps",
    ],
    ROLE_DEVELOPER: [
        "saas.view_billing",
        "buckets.view_storage",
        "buckets.upload_files",
        "buckets.view_apps",
        "buckets.deploy_apps",
        "buckets.control_apps",
    ],
    ROLE_VIEWER: [
        "saas.view_billing",
        "buckets.view_storage",
        "buckets.view_apps",
    ],
}

# ---------------------------------------------------------------------------
# Industrial Capabilities List (for UI management)
# ---------------------------------------------------------------------------
MANAGEMENT_PERMISSIONS = [
    ("saas.manage_members", "Team Management"),
    ("saas.view_billing", "View Infrastructure Quotas/Billing"),
    ("saas.manage_billing", "Manage Subscriptions"),
    ("saas.destroy_organization", "Delete Organization"),
    ("buckets.view_storage", "View Storage Hubs"),
    ("buckets.manage_buckets", "Manage Storage Hubs"),
    ("buckets.upload_files", "Manage Storage Objects"),
    ("buckets.view_apps", "View Compute Fleet"),
    ("buckets.manage_apps", "Provision/Manage Apps"),
    ("buckets.deploy_apps", "Deploy Code Artifacts"),
    ("buckets.control_apps", "Start/Stop Edge Processes"),
]

def has_org_permission(user, org, permission_name):
    """
    Core RBAC Resolver (Dynamic). 
    Checks if a user has a specific permission within an organization.
    Prioritizes DB-backed Custom Roles, falls back to static Role Map.
    """
    if not user.is_authenticated or not org:
        return False
        
    # Superusers bypass tenant checks
    if user.is_superuser:
        return True
        
    # Org Owner bypasses tenant checks for their own org
    if org.owner_id == user.id:
        return True

    # Look up membership
    try:
        from saas.models import TeamMember, RolePermission
        membership = TeamMember.objects.select_related('role_obj').get(user=user, org=org)
        
        # 1. Check Dynamic DB-backed Role
        if membership.role_obj:
            return RolePermission.objects.filter(
                role=membership.role_obj, 
                permission_codename=permission_name
            ).exists()
            
        # 2. Fallback to Static Code-based Role Mapping (Transition Phase)
        allowed_permissions = ROLE_PERMISSION_MAP.get(membership.role, [])
        return permission_name in allowed_permissions

    except TeamMember.DoesNotExist:
        return False
