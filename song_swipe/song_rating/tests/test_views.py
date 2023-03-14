import environ
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from spotipy.oauth2 import SpotifyOAuth

# from song_swipe.song_rating.views import GetSongView

env = environ.Env()


class TestGetSongView(TestCase):
    def setUp(self) -> None:
        self.spotify_identity = SpotifyOAuth(
            client_id=env("SPOTIFY_CLIENT_ID"),
            client_secret=env("SPOTIFY_CLIENT_SECRET"),
            redirect_uri="http://localhost:8000/accounts/spotify/login/callback/",
            scope=[
                "user-library-read",
                "user-library-modify",
                "streaming",
                "user-read-recently-played",
                "user-read-private",
            ],
        )

    def test_unauthorized_access(self):
        url = reverse("song_rating:song")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_song_view_returns_right_song(self):
        pass
        # song_from_view = self.client.get('song/')
        # self.assertEqual(song_from_view, )
