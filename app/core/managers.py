from __future__ import annotations

from typing import Type

from django.contrib.auth.models import User
from django.db import models
from django.db.models import QuerySet


# Manager class that is applied to the ObjectPermission model
# Adds additional model methods that potentially operate on multiple instances of ObjectPermission
class ObjectPermissionManager(models.Manager):
    def get_objects_for_user(
        self, model_class: Type[models.Model], user, perms: list[str]
    ) -> QuerySet:
        if len(perms) <= 0:
            return model_class.objects.none()

        # Convert user to a User object if it's a string or integer
        if isinstance(user, str) or isinstance(user, int):
            user = User.objects.get(
                pk=user if isinstance(user, int) else None,
                username=user if isinstance(user, str) else None,
            )

        all_ids = self.filter(
            user=user, content_type=model_class.content_type, permission__in=perms
        ).values_list("object_id", flat=True)

        return model_class.objects.filter(pk__in=all_ids)

    def clear_all_for_object(self, obj):
        if hasattr(obj, "permissions"):
            obj.permissions.all().delete()
