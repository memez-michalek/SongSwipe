from django.urls import path

from .views import SpotifyLogin

app_name = "song_rating"

urlpatterns = [path("spotify/", SpotifyLogin.as_view(), name="spotify_login")]
