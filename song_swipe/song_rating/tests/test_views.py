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

        self.reverse_url = reverse("song_rating:song")

    def test_unauthorized_access(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_song_view_returns_song(self):
        self.setUp()
        """response = requests.get(
            url="https://api.spotify.com/v1/me/",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify_access_token['access_token']}",
            },
        )
        logging.critical(response)
        """
        response = self.client.get(self.reverse_url, headers={""})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLikeView(TestCase):
    def setUp(self):
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

        self.reverse_url = reverse("song_rating:like_song")
        self.test_song_spotify_ids = "60g27TTTjDXJyL36I592VK"

    def test_unauthorized_access_attempt(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_song_was_liked(self):
        response = self.client.get(
            self.reverse_url, {"spotify_id": self.test_song_spotify_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = requests.get(
            f"https://api.spotify.com/v1/me/tracks/contains?ids={self.test_song_spotify_ids}",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotify_access_token['access_token']}",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response, True)
