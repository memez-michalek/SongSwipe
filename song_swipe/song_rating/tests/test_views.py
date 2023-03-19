import logging

import environ
import requests
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from spotipy.oauth2 import SpotifyOAuth

# from song_swipe.users.models import User

# from song_swipe.song_rating.views import GetSongView

env = environ.Env()


class BaseTestCase(TestCase):
    spotify_access_token = None

    @classmethod
    def setUpClass(cls):
        if cls.spotify_access_token is None:
            oauth_manager = SpotifyOAuth(
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
            auth_url = oauth_manager.get_authorize_url()
            # At this point, you will need to open auth_url in a browser to authenticate
            # with Spotify and authorize your app
            print(auth_url)
            authorization_code = input("Enter the authorization code: ")
            cls.spotify_access_token = oauth_manager.get_access_token(
                authorization_code
            )["access_token"]

            """
            try:
                user = User.objects.get(username="testuser")
            except User.DoesNotExist:
                user = User.objects.create(username="testuser")
                SocialToken.objects.create(
                    app_id=1,
                    account = user.socialaccount_set.create(provider='spotify'),
                    token = cls.spotify_access_token,
                )

            """

    @classmethod
    def tearDownClass(cls):
        cls.spotify_access_token = None

    """
    def get_access_token(self) -> None:
        oauth_manager = SpotifyOAuth(
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
        auth_url = oauth_manager.get_authorize_url()
        # At this point, you will need to open auth_url in a browser to authenticate
        # with Spotify and authorize your app
        print(auth_url)
        authorization_code = input("Enter the authorization code: ")
        spotify_access_token = oauth_manager.get_access_token(
            authorization_code
        )
        return spotify_access_token
        """


class TestGetSongView(BaseTestCase):
    def setUp(self):
        # self.spotify_access_token = self.get_access_token()
        self.reverse_url = reverse("song_rating:song")

    def test_unauthorized_access(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_song_view_returns_song(self):
        self.setUp()
        response = self.client.get(
            self.reverse_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {self.spotify_access_token}",
            },
        )
        logging.critical(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLikeView(BaseTestCase):
    def setUp(self):
        # self.spotify_access_token = self.get_spotify_access_token()
        self.genres = "polish hip hop"
        self.spotify_artist_id = "2GzZAv52VCMdVli7QzkteT"
        self.test_song_spotify_ids = "60g27TTTjDXJyL36I592VK"

        self.reverse_url = (
            f"{reverse('song_rating:like_song', kwargs={'slug': self.test_song_spotify_ids})}"
            f"?spotify_artist_id={self.spotify_artist_id}"
            f"&genres={self.genres}"
        )

    def test_unauthorized_access_attempt(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_song_was_liked(self):
        response = self.client.get(
            self.reverse_url,
            headers={
                "Authorization": f"Bearer {self.spotify_access_token}",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = requests.get(
            f"https://api.spotify.com/v1/me/tracks/contains?ids={self.test_song_spotify_ids}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify_access_token}",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestHateView(BaseTestCase):
    def setUp(self):
        # self.spotify_access_token = self.get_spotify_access_token()
        self.genres = "polish hip hop"
        self.spotify_artist_id = "2GzZAv52VCMdVli7QzkteT"
        self.test_song_spotify_ids = "60g27TTTjDXJyL36I592VK"

        self.reverse_url = (
            f"{reverse('song_rating:like_song', kwargs={'slug': self.test_song_spotify_ids})}"
            f"?spotify_artist_id={self.spotify_artist_id}"
            f"&genres={self.genres}"
        )

    def test_unauthorized_access_attempt(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_song_hated(self):
        response = self.client.get(
            self.reverse_url,
            headers={
                "Authorization": f"Bearer {self.spotify_access_token}",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = requests.get(
            f"https://api.spotify.com/v1/me/tracks/contains?ids={self.test_song_spotify_ids}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify_access_token}",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
