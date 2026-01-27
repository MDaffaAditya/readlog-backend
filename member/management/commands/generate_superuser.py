import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from member.models import User


class Command(BaseCommand):
    help = "Generate Superuser"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", None)
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", None)
        is_admin_exists = User.objects.filter(
            username=username, email=email, is_superuser=True
        ).exists()
        if not is_admin_exists:
            call_command("createsuperuser", "--noinput")
