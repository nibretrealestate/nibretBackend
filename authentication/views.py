from rest_framework import viewsets
from rest_framework import permissions

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from authentication.models import *
from authentication.serializers import UserAccountSerialzer



class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter 
    client_class = OAuth2Client

class AgentsView(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerialzer
    permission_classes = [permissions.IsAdminUser]

