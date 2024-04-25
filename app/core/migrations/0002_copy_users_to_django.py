from datetime import datetime

from django.db import migrations, IntegrityError, transaction

from django.contrib.auth.models import User as DjangoUser

# from core.models import Users


def copy_users_to_django(apps, schema_editor):
    """
    Copy old Fuel Users model to Django's User model
    """
    # TODO: figure out how to handle password and login_hash
    # TODO: figure out how to handle profile_fields
    # TODO: look into bulk_create for potential efficiency

    FuelUsers = apps.get_model("core", "Users")

    for fuel_user in FuelUsers.objects.all():
        # convert created_at and last_login to datetime
        date_joined = datetime.fromtimestamp(fuel_user.created_at)
        last_login = datetime.fromtimestamp(fuel_user.last_login)

        if not fuel_user.username:
            fuel_user.username = f"{fuel_user.id}{fuel_user.first}{fuel_user.last}"

        try:
            with transaction.atomic():
                new_user = DjangoUser.objects.create(
                    id=fuel_user.id,
                    password=fuel_user.password,
                    last_login=last_login,
                    is_superuser=False,
                    username=fuel_user.username,
                    first_name=fuel_user.first,
                    last_name=fuel_user.last,
                    email=fuel_user.email,
                    is_staff=False,
                    is_active=True,
                    date_joined=date_joined,
                )
                new_user.save()
        except IntegrityError:
            # duplicate username, make a new one
            fuel_user.username = (
                f"{fuel_user.username}_{fuel_user.id}{fuel_user.first}{fuel_user.last}"
            )
            new_user = DjangoUser.objects.create(
                id=fuel_user.id,
                password=fuel_user.password,
                last_login=last_login,
                is_superuser=False,
                username=fuel_user.username,
                first_name=fuel_user.first,
                last_name=fuel_user.last,
                email=fuel_user.email,
                is_staff=False,
                is_active=True,
                date_joined=date_joined,
            )
            new_user.save()


def revert_django_users_to_empty(apps, schema_editor):
    # delete all Django User objects
    try:
        DjangoUser.objects.all().delete()
    except Exception:
        pass


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [
        migrations.RunPython(copy_users_to_django, revert_django_users_to_empty)
    ]
