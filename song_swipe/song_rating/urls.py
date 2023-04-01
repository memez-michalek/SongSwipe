from django.urls import path

from .views import GetFirstSongView, HateSongView, LikeSongView, SpotifyLogin

# from .adapters import spotify_callback
app_name = "song_rating"

urlpatterns = [
    path("spotify/", SpotifyLogin.as_view(), name="spotify_login"),
    path("song/", GetFirstSongView.as_view({"get": "list"}), name="song"),
    # path('spotify/login/callback/', spotify_callback, name='spotify_callback'),
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
