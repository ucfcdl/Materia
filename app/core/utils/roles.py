from django.contrib.auth.models import AnonymousUser, User


# these are effectively methods that should be part of the User model or part of a custom manager
# however, given we're not extended or implementing our own User model,
# we can't really define a custom manager. This is the next best solution but
# would be worth revisiting in the future.
class RolesUtil:

    @staticmethod
    def user_is_student(user: User):
        return not RolesUtil.does_user_have_roles(user, ["basic_author", "super_user"])

    # Returns True if user has at least one of the roles specified
    @staticmethod
    def does_user_have_roles(
        user: User | AnonymousUser, roles: str | list[str]
    ) -> bool:
        # Check if user is not logged in
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False

        # Convert to list if single string passed in
        if type(roles) is str:
            roles = [roles]

        # Empty list of roles, just return true
        if not roles:
            return True

        # Check to see if any of the roles are present
        return user.groups.filter(name__in=roles).exists()

    @staticmethod
    def is_superuser_or_elevated(user: User) -> bool:
        if not user or not user.is_authenticated:
            return False

        return user.is_superuser or user.groups.filter(name="support_user").exists()
