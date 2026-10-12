import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Create the configured deployment superuser if it does not exist."

    def handle(self, *args, **options):
        user_model = get_user_model()
        env_names = {
            field_name: f"DJANGO_SUPERUSER_{field_name.upper()}"
            for field_name in (user_model.USERNAME_FIELD, *user_model.REQUIRED_FIELDS)
        }
        env_names["password"] = "DJANGO_SUPERUSER_PASSWORD"
        user_data = {
            name: os.environ.get(env_name, "")
            for name, env_name in env_names.items()
        }

        configured_values = [value.strip() for value in user_data.values()]
        if not any(configured_values):
            self.stdout.write("Superuser bootstrap skipped; no credentials configured.")
            return
        if any(not value for value in configured_values):
            missing = ", ".join(
                env_name
                for name, env_name in env_names.items()
                if not user_data[name].strip()
            )
            raise CommandError(
                f"Missing required superuser environment variables: {missing}"
            )
        if not settings.DEBUG and connection.vendor == "sqlite":
            raise CommandError(
                "Superuser bootstrap requires a persistent database; "
                "configure DATABASE_URL."
            )

        username_field = user_model.USERNAME_FIELD
        create_data = {
            key: value
            for key, value in user_data.items()
            if key != "password"
        }
        try:
            for field_name, value in create_data.items():
                field = user_model._meta.get_field(field_name)
                create_data[field_name] = field.clean(value, None)
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error

        username = create_data[username_field]
        manager = user_model._default_manager
        if manager.filter(**{username_field: username}).exists():
            self.stdout.write("Configured superuser already exists; no changes made.")
            return

        try:
            validate_password(user_data["password"], user_model(**create_data))
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error

        manager.db_manager().create_superuser(
            **create_data,
            password=user_data["password"],
        )
        self.stdout.write("Configured superuser created successfully.")
