import logging

import environ
import requests
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from spotipy.oauth2 import SpotifyOAuth

# from song_swipe.song_rating.views import GetSongView

env = environ.Env()


class TestGetSongView(TestCase):
    def setUp(self) -> None:
        self.oauth_manager = SpotifyOAuth(
            client_id=env("SPOTIFY_CLIENT_ID"),
            client_secret=env("SPOTIFY_CLIENT_SECRET"),
            redirect_uri="http://localhost:8000/callback/test",
            scope=[
                "user-library-read",
                "user-library-modify",
                "streaming",
                "user-read-recently-played",
                "user-read-private",
                "user-read-email",
                "user-top-read",
            ],
        )
        auth_url = self.oauth_manager.get_authorize_url()
        # At this point, you will need to open auth_url in a browser to authenticate
        # with Spotify and authorize your app
        print(auth_url)
        authorization_code = input("Enter the authorization code: ")
        self.spotify_access_token = self.oauth_manager.get_access_token(
            authorization_code
        )

    def test_unauthorized_access(self):
        url = reverse("song_rating:song")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_song_view_returns_right_song(self):
        self.setUp()
        response = requests.get(
            url="https://api.spotify.com/v1/me/player",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify_access_token['access_token']}",
            },
        )
        logging.critical(response)

        # song_from_view = self.client.get('song/')
        # self.assertEqual(song_from_view, )
