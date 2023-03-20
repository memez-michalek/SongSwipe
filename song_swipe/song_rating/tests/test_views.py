import logging
from unittest.mock import patch

import environ
import requests
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from spotipy.oauth2 import SpotifyOAuth

from song_swipe.song_rating.views import UtilsMixin

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


class TestUtilsMixin(TestCase):
    def test_get_genre(self):
        access_token = "12345"
        artist_seed = "6vWDO969PvNqNYHIOW5v0m"
        expected_response = ["pop", "pop rock"]
        with patch("requests.get") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = {"genres": expected_response}
            response = UtilsMixin.get_genre(UtilsMixin(), artist_seed, access_token)
        self.assertEqual(response, expected_response)

    def test_get_genre_failed_request(self):
        access_token = "12345"
        artist_seed = "6vWDO969PvNqNYHIOW5v0m"
        expected_response = Response(
            "could not gather genre", status=status.HTTP_404_NOT_FOUND
        )
        with patch("requests.get") as mock_request:
            mock_request.return_value.status_code = 404
            mock_request.return_value.json.return_value = {"genres": []}
            response = UtilsMixin.get_genre(UtilsMixin(), artist_seed, access_token)
        self.assertEqual(response.data, expected_response.data)
        self.assertEqual(response.status_code, expected_response.status_code)

    def test_get_users_spotify_id(self):
        access_token = "12345"
        expected_response = "spotifyuser1234"
        with patch("requests.get") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = {"id": expected_response}
            response = UtilsMixin.get_users_spotify_id(UtilsMixin(), access_token)
        self.assertEqual(response, expected_response)

    def test_get_users_spotify_id_failed_request(self):
        access_token = "12345"
        expected_exception = ValueError("responses status code is different than 200")
        with patch("requests.get") as mock_request:
            mock_request.return_value.status_code = 404
            mock_request.return_value.json.return_value = {}
            with self.assertRaises(Exception) as context:
                UtilsMixin.get_users_spotify_id(UtilsMixin(), access_token)
            self.assertEqual(str(context.exception), str(expected_exception))

    def test_add_song_to_playlist(self):
        access_token = "12345"
        playlist_id = "123"
        track_uri = "spotify:track:1T7hUnFdDTjNFPXV37yOaB"
        expected_response = True
        with patch("requests.post") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = {}
            response = UtilsMixin.add_song_to_playlist(
                UtilsMixin(), access_token, playlist_id, track_uri
            )
        self.assertEqual(response, expected_response)

    def test_add_song_to_playlist_failed_request(self):
        access_token = "12345"
        playlist_id = "123"
        track_uri = "spotify:track:1T7hUnFdDTjNFPXV37yOaB"
        expected_exception = ValueError("responses status code is different than 200")
        with patch("requests.post") as mock_request:
            mock_request.return_value.status_code = 404
            mock_request.return_value.json.return_value = {}
            with self.assertRaises(Exception) as context:
                UtilsMixin.add_song_to_playlist(
                    UtilsMixin(), access_token, playlist_id, track_uri
                )
            self.assertEqual(str(context.exception), str(expected_exception))
