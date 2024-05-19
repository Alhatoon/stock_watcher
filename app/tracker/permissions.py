# permissions.py

from rest_framework.permissions import BasePermission
from cassandra.cqlengine.query import DoesNotExist
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Token, CustomUser

class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Write permissions are only allowed to the owner of the object.
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('Authorization header missing')

        try:
            token_obj = Token.objects.get(token=token)
            user_email = token_obj.user_email
            user = CustomUser.objects.get(email=user_email)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        return obj.user_email == user_email

class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return None

        try:
            token_obj = Token.objects.get(token=token)
            user_email = token_obj.user_email
            user = CustomUser.objects.get(email=user_email)
            return (user, None)
        except DoesNotExist:
            raise AuthenticationFailed(f'Invalid token')
