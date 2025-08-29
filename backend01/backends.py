# backend01/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import UserInfo

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, account=None, password=None, **kwargs):
        try:
            user = UserInfo.objects.get(account=account)
            if user.check_password(password):
                return user
        except UserInfo.DoesNotExist:
            return None
        return None