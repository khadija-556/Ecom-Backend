from rest_framework.authentication import get_authorization_header
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django.conf import settings
from .models import *
import datetime
import jwt

class CustomAuthenticationFailed(APIException):
    status_code = 401
    default_detail = 'Authentication failed.'
    default_code = 'authentication_failed'

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail, code)


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = None

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            token = request.COOKIES.get('ecom_access_token')

        if not token:
            raise CustomAuthenticationFailed({
                'status': 'error',
                'message': 'Authentication credentials were not provided.',
            }, status_code=401)
        
        try:
            payload = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'] ,algorithms=settings.SIMPLE_JWT['ALGORITHMS'])
        
        except jwt.ExpiredSignatureError:
            raise CustomAuthenticationFailed({
                'status': 'error',
                'message': 'Token has expired',
            }, status_code=401)
        except jwt.DecodeError:
            raise CustomAuthenticationFailed({
                'status': 'error',
                'message': 'Invalid token',
            }, status_code=401)
        
        user = CustomUser.objects.get(id=payload['user_id'])
        if not user:
            raise AuthenticationFailed('User not found')
        if not user.is_active:
            raise AuthenticationFailed('User is inactive')
        
        return(user, None)