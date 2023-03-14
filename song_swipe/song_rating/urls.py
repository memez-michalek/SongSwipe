from django.urls import path

from .views import GetSongView, SpotifyLogin

app_name = "song_rating"

urlpatterns = [
    path("spotify/", SpotifyLogin.as_view(), name="spotify_login"),
    path("song/", GetSongView.as_view({"get": "list"}), name="song"),
]
