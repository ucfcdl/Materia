import logging

from core.models import Asset, ObjectPermission, Question, WidgetInstance
from core.utils.roles import RolesUtil
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions

logger = logging.getLogger("django")


class DenyAll(permissions.BasePermission):
    def has_permission(self, request, view):
        return False


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsSuperOrSupportUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return RolesUtil.is_superuser_or_elevated(request.user)


class IsSelfOrElevatedAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            RolesUtil.is_superuser_or_elevated(request.user)
            or obj.id == request.user.id
        )


# Asks if a user has *any* perms at all on an object (or is elevated)
class HasPermsOrElevatedAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        elif RolesUtil.is_superuser_or_elevated(request.user):
            return True
        else:
            if (
                isinstance(obj, WidgetInstance)
                or isinstance(obj, Question)
                or isinstance(obj, Asset)
            ):
                return obj.permissions.filter(
                    Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()),
                    user=request.user,
                ).exists()
            else:
                return False


class IsSuperuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class CanCreateWidgetInstances(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user is None or RolesUtil.does_user_have_roles(user, "no_author"):
            return False
        return True


class HasFullPermsOrElevated(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        # False if user isn't logged in
        if not user or not user.is_authenticated:
            return False

        # True if is elevated user
        if RolesUtil.is_superuser_or_elevated(request.user):
            return True

        # Otherwise, check if user has full perms on this object
        if hasattr(obj, "permissions"):
            return obj.permissions.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()),
                user=request.user,
                permission=ObjectPermission.PERMISSION_FULL,
            ).exists()


class HasFullPermsOrElevatedOrReadOnly(HasFullPermsOrElevated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_object_permission(request, view, obj)


class HasFullInstancePermsAndLockOrElevated(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, WidgetInstance):
            return False

        user = request.user

        # False if user isn't logged in
        if not user or not user.is_authenticated:
            return False

        # True if is elevated user
        if RolesUtil.is_superuser_or_elevated(request.user):
            return True

        # Make sure the widget isn't locked
        # The frontend should stop users from editing if locked, but this is here *just in case*
        if not obj.lock_available_to_user(user):
            return False

        # Otherwise, check if user has full perms on this object
        if hasattr(obj, "permissions"):
            return obj.permissions.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()),
                user=request.user,
                permission=ObjectPermission.PERMISSION_FULL,
            ).exists()
