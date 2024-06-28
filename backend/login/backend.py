import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from rest_framework import status
from rest_framework.response import Response
from .models import CustomUser as User

class SSOAuthenticationBackend(BaseBackend):

    def authenticate(self, request, sso_token=None):
        if sso_token is None:
            return None

        user_info = self.validate_sso_token(sso_token)

        if user_info and not isinstance(user_info, Response):
            try:
                user = User.objects.get(email=user_info['email'])
            except User.DoesNotExist:
                roles = user_info.get('roles', [])
                user_role = 'user'
                is_member = any(role['role'].lower() != 'user' for role in roles)
                for role in roles:
                    if role['role'].lower() != 'user':
                        user_role = role['role']
                        break
                user = User.objects.create(
                    id=user_info['rollNo'],
                    email=user_info['email'],
                    name=user_info['name'],
                    phone_no=user_info['phone'],
                    position=user_role,
                    is_member=is_member,
                )
                user.set_unusable_password()
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def validate_sso_token(self, sso_token):
        jwt_secret = settings.JWT_SECRET_KEY
        
        try:
            payload = jwt.decode(sso_token, jwt_secret, algorithms=['HS256'])
            return payload
        except ExpiredSignatureError:
            return Response({'error': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidTokenError:
            return Response({'error': 'Invalid Cred'}, status=status.HTTP_400_BAD_REQUEST)
