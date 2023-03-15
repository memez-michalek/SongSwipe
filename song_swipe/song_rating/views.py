import logging

import requests
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import viewsets


class SpotifyLogin(SocialLoginView):
    adapter_class = SpotifyOAuth2Adapter
    # client_class = OAuth2Client


class GetSongView(viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        """
        IDEAS HOW TO IMPLEMENT ALGORITHM FOR SHOWING USER NEW FRESH SONGS
        1 GET RECENTLY PLAYED ARTIST
        2 GET SIMILAR ARTISTS TO RECENTLY PLAYED
        3 THEN GET THE MOST POPULAR TRACK FROM THAT ARTIST
        :REPEAT
        4 GET THE MOST RELATED SONG TO CURRENTLY PLAYED SONG


        """

        # app = SocialApp.objects.get(provider="spotify")
        user = SocialAccount.objects.get(user=request.user)
        logging.critical(user)
        users_access_token = user.socialtoken_set.first()
        logging.critical(users_access_token)
        response = requests.get(
            "https://api.spotify.com/v1/me/top/artists",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {users_access_token.token}",
            },
        )
        logging.info(response)
