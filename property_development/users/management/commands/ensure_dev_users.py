import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Create a default development superuser and two test users (idempotent). NOT for production."

    def add_arguments(self, parser):
        parser.add_argument("--reset-password", action="store_true",
                            help="Reset passwords even if users already exist")

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        reset = options["reset_password"]

        # --- 1) Superuser ---
        su_username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        su_email    = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        su_password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")

        su, created = User.objects.get_or_create(
            username=su_username,
            defaults={"email": su_email, "is_staff": True, "is_superuser": True},
        )
        if created:
            su.set_password(su_password)
            su.save()
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {su_username} / {su_email}"))
        else:
            # Ensure flags are correct
            changed = False
            if not su.is_staff:
                su.is_staff = True; changed = True
            if not su.is_superuser:
                su.is_superuser = True; changed = True
            if reset:
                su.set_password(su_password); changed = True
            if changed:
                su.save()
                self.stdout.write(self.style.SUCCESS(f"Updated superuser: {su_username}"))
            else:
                self.stdout.write(f"Superuser already exists: {su_username}")

        # --- 2) Test users (regular) ---
        # Defaults can be overridden via env if you like
        users_spec = [
            {
                "username": os.getenv("TEST_USER1_USERNAME", "investor_one"),
                "email":    os.getenv("TEST_USER1_EMAIL",    "investor_one@example.com"),
                "password": os.getenv("TEST_USER1_PASSWORD", "test1234"),
            },
            {
                "username": os.getenv("TEST_USER2_USERNAME", "investor_two"),
                "email":    os.getenv("TEST_USER2_EMAIL",    "investor_two@example.com"),
                "password": os.getenv("TEST_USER2_PASSWORD", "test1234"),
            },
        ]

        for spec in users_spec:
            u = User.objects.filter(username=spec["username"]).first()
            if not u:
                u = User.objects.create_user(
                    username=spec["username"],
                    email=spec["email"],
                    password=spec["password"],
                )
                # Explicitly ensure they are NOT staff/superuser
                u.is_staff = False
                u.is_superuser = False
                u.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Created test user: {spec['username']} / {spec['email']} (pwd: {spec['password']})"
                ))
            else:
                changed = False
                # Make sure they are regular users
                if u.is_staff or u.is_superuser:
                    u.is_staff = False
                    u.is_superuser = False
                    changed = True
                if reset:
                    u.set_password(spec["password"])
                    changed = True
                if changed:
                    u.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated test user: {spec['username']}"))
                else:
                    self.stdout.write(f"Test user already exists: {spec['username']}")

        self.stdout.write(self.style.NOTICE(
            "Done. Assign projects via Project.allowed_investors in admin to test authorization."
        ))
