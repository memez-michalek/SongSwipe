from allauth.socialaccount.models import SocialToken
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SpotifyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.META.get("authentication")
        print(access_token)
        try:
            social_token = SocialToken.objects.get(token=access_token)
        except SocialToken.DoesNotExist:
            raise AuthenticationFailed("Access token does not exist")

        if social_token.account.provider != "spotify":
            raise AuthenticationFailed("invalid account provider")

        return (social_token.account.user, None)
