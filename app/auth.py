from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

class BackupAuth(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization')

        if not auth:
            raise AuthenticationFailed("Missing Authorization header")
        
        if not auth.startswith("Bearer "):
            raise AuthenticationFailed("Invalid auth scheme")
        
        token = auth.split(" ", 1)[1].strip()

        if not token:
            raise AuthenticationFailed("Missing token")
        
        if token != settings.BACKUP_TOKEN:
            raise AuthenticationFailed("Invalid token")

        return (AnonymousUser(), None)