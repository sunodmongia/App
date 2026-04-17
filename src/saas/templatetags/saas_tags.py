from django import template
from saas.permissions import has_org_permission
from saas.models import TeamMember

register = template.Library()

@register.filter(name='has_org_perm')
def has_org_perm(user, arg_string):
    """
    Usage: {% if user|has_org_perm:"org,buckets.add_app" %}
    Note: Requires organization and permission name as a comma-separated string.
    """
    try:
        org_obj, perm_name = arg_string.split(',')
        return has_org_permission(user, org_obj, perm_name)
    except (ValueError, AttributeError):
        return False

@register.simple_tag
def get_user_role(user, org):
    """
    Returns the display name of the user's role in the organization.
    Prioritizes DB-backed role_obj.
    """
    if not user.is_authenticated or not org:
        return "Viewer"
    
    if org.owner_id == user.id:
        return "Owner"
        
    try:
        membership = TeamMember.objects.select_related('role_obj').get(user=user, org=org)
        if membership.role_obj:
            return membership.role_obj.name
        return membership.get_role_display()
    except TeamMember.DoesNotExist:
        return "Viewer"
