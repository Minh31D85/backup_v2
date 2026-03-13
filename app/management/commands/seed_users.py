from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import os

User = get_user_model()

class Command(BaseCommand):
    help =  "Erstell Standard Benutzer"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        username = os.environ.get("SUPERUSER_USERNAME")
        password = os.environ.get("SUPERUSER_PASSWORD")
        email = os.environ.get("SUPERUSER_EMAIL")

        if not username or not password or not email:
            self.stdout.write(self.style.ERROR("Environment variable is missing"))
            return
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING("user exists"))
            return
        
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(self.style.SUCCESS("superuser created"))