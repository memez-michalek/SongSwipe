from django.urls import path

from .views import GetFirstSongView, HateSongView, LikeSongView, SpotifyLogin

app_name = "song_rating"

urlpatterns = [
    path("spotify/", SpotifyLogin.as_view(), name="spotify_login"),
    path("song/", GetFirstSongView.as_view({"get": "list"}), name="song"),
    path(
        "like_song/<slug:slug>/",
        LikeSongView.as_view({"get": "retrieve"}),
        name="like_song",
    ),
    path(
        "hate_song/<slug:slug>/",
        HateSongView.as_view({"get": "retrieve"}),
        name="hate_song",
    ),
]
