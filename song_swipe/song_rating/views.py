import logging

import requests
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import viewsets


class SpotifyLogin(SocialLoginView):
    adapter_class = SpotifyOAuth2Adapter


class GetSongView(viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        logging.debug(request.user)
        users_access_token = SocialToken.objects.get(
            account__user=request.user, account__provider="spotify"
        ).token

        response = requests.get(
            "https://api.spotify.com/v1/me/top/artists",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {users_access_token}",
            },
        )
        logging.info(response)
