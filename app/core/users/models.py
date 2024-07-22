import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import models

logger = logging.getLogger(__name__)

class User(AbstractUser):
    """
    Custom user model for Materia.
    """
    # The user's preferred first name.
    # display_name = models.CharField(max_length=255, blank=True, null=True)

    # TODO USERNAME_FIELD
    # TODO EMAIL_FIELD
    # TODO REQUIRED_FIELDS

    def sync_ad_attributes(self, attributes: dict) -> None:
        """
        Update a user's attributes with data from Active Directory.

        :param attributes: The attribute mapping to apply to the user.
        """
        for key, value in settings.SAML_ATTRIBUTE_MAPPING.items():
            try:
                field = value[0]
                attribute_value = attributes.get(key)

                # Don't override the user's username
                if field == "username":
                    continue

                # Most values are sent as an array. For example, a lookup to
                # attributes.get("email") will return something like
                # ["this@example.com"].
                #
                # We need to extract the first element of this array
                # to get a usable value.
                if isinstance(attribute_value, list):
                    attribute_value = attribute_value[0]

                setattr(self, field, attribute_value)
                logger.debug("Set `user.%s=%s`", field, attribute_value)
            except Exception:  # pylint: disable=broad-except
                logger.debug("Unable to set `user.%s`", key)

        self.save()
