from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Profile


class PhoneOrUsernameBackend(ModelBackend):
    """Allow authentication by phone number or username (for legacy accounts)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None

        # First try exact username match (legacy accounts and phone-as-username).
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None