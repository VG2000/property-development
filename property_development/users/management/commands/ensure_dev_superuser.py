# users/management/commands/ensure_dev_superuser.py
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

class Command(BaseCommand):
    help = "Create/update a DEV superuser if it doesn't exist. NOT for production."

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.getenv("DEV_SUPERUSER_USERNAME", "vgomez"))
        parser.add_argument("--email", default=os.getenv("DEV_SUPERUSER_EMAIL", "vgomez@example.com"))
        parser.add_argument("--password", default=os.getenv("DEV_SUPERUSER_PASSWORD", "admin"))
        parser.add_argument("--reset-password", action="store_true", help="Reset password even if user exists")

    @transaction.atomic
    def handle(self, *args, **opts):
        User = get_user_model()
        username_field = User.USERNAME_FIELD  # 'username' in default User, 'email' for some custom users
        username_value = opts["username"]
        email_value = opts["email"]
        password = opts["password"]
        reset_password = opts["reset_password"]

        # If the username field is 'email', make sure we pass an email-looking value
        if username_field == "email":
            username_value = email_value

        # Try to find by the model's username field
        try:
            user = User.objects.get(**{username_field: username_value})
            changed = False
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                changed = True
            if reset_password or not user.has_usable_password():
                user.set_password(password)
                changed = True
            if changed:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated existing superuser: {username_value}"))
            else:
                self.stdout.write(f"Superuser already exists and is up-to-date: {username_value}")
            return
        except User.DoesNotExist:
            pass

        # Build kwargs for create_superuser
        create_kwargs = {username_field: username_value, "email": email_value}
        # Handle any REQUIRED_FIELDS a custom user might have
        for field in getattr(User, "REQUIRED_FIELDS", []):
            create_kwargs.setdefault(field, os.getenv(f"DEV_SUPERUSER_{field.upper()}", "admin"))

        user = User.objects.create_superuser(password=password, **create_kwargs)
        self.stdout.write(self.style.SUCCESS(f"Created superuser: {getattr(user, username_field)}"))
