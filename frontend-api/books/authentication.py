from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class InterServiceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Token '):
            return None
        
        token = auth_header.split(' ')[1]
        
        if token != settings.INTER_SERVICE_TOKEN:
            raise AuthenticationFailed('Invalid token')
        
        return (None, None)