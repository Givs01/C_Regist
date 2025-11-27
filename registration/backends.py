from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import UsersData

class CustomUserBackend(BaseBackend):
    """
    Authenticate against Django's User table and custom UsersData table.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1. Try default User (admin)
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

        # 2. Try custom UsersData
        try:
            custom_user = UsersData.objects.get(userId=username)
            if check_password(password, custom_user.password):
                # Create a temporary User object to allow login()
                user = User(
                    username=custom_user.userId,
                    first_name=custom_user.name,
                    is_staff=False,
                    is_active=True,
                )
                user.set_unusable_password()  # So password can't be used for default login
                # Attach custom user id for reference
                user.custom_user_id = custom_user.id
                return user
        except UsersData.DoesNotExist:
            return None

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

