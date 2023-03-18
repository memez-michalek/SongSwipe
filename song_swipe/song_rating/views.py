import logging
import random

import requests
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import SongSerializer


class UtilsMixin:
    def get_genre(self, artist_seed, access_token):
        response = requests.get(
            f"https://api.spotify.com/v1/artists/{artist_seed}",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        if response.status_code != 200:
            return Response("could not gather genre", status=status.HTTP_404_NOT_FOUND)

        return response.json()["genres"]


class SpotifyLogin(SocialLoginView):
    adapter_class = SpotifyOAuth2Adapter
    # client_class = OAuth2Client


class GetFirstSongView(UtilsMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        """
        IDEAS HOW TO IMPLEMENT ALGORITHM FOR SHOWING USER NEW FRESH SONGS
        1 GET RECENTLY PLAYED ARTIST/TRACK AND GENERES
        2 GET THE MOST RELATED SONG TO RECENTLY PLAYED SONG

        """

        # app = SocialApp.objects.get(provider="spotify")
        access_token = SocialToken.objects.get(
            app__provider="spotify", account__user=request.user
        )
        logging.critical(access_token)
        response = requests.get(
            "https://api.spotify.com/v1/me/top/tracks",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        logging.critical(response)
        if response.status_code != 200:
            return Response("Error Found", status=response.status_code)

        top_tracks = response.json()
        first_track = top_tracks["items"][random.randint(0, 9)]

        artist_seed = first_track["album"]["artists"][0]["id"]
        artist_name = first_track["album"]["artists"][0]["name"]
        track_name = first_track["name"]
        track_id = first_track["id"]
        preview_url = first_track["preview_url"]
        images = first_track["album"]["images"]
        genres = self.get_genre(artist_seed, access_token)

        serialized = SongSerializer(
            {
                "artist_seed": artist_seed,
                "artist_name": artist_name,
                "track_name": track_name,
                "track_id": track_id,
                "preview_url": preview_url,
                "images": images,
                "genres": genres,
            }
        )

        return Response(data=serialized.data)


class LikeSongView(UtilsMixin, viewsets.GenericViewSet):
    # BY DEFAULT LIKE/HATE/IGNORE SONG RETURNS NEXT SONG AND STATUS IF
    # SONG HAS BEEN ADDED SUCCESSFULY

    def retrieve(self, request, slug, *args, **kwargs):
        # spotify_song_id = self.kwargs.get("spotify_song_id")
        spotify_song_id = slug
        access_token = SocialToken.objects.get(
            app__provider="spotify", account__user=request.user
        )
        genres = request.query_params.get("genres")
        spotify_artist_id = request.query_params.get("spotify_artist_id")

        response = requests.put(
            f"https://api.spotify.com/v1/me/tracks?ids={spotify_song_id}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        logging.critical(response)

        if response.status_code != 200:
            return Response("Could not add selected track")

        url = (
            "https://api.spotify.com/v1/recommendations"
            "?limit=10"
            "&market=PL"
            f"&seed_artists={spotify_artist_id}"
            f"&seed_genres={genres}"
            f"&seed_tracks={spotify_song_id}"
        )

        logging.critical(url)

        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )
        logging.critical(response.status_code)
        logging.critical(response.text)

        if response.status_code != 200:
            return Response("Could not recommend next track")

        # RETRIEVE DATA FROM RESPONSE
        top_tracks = response.json()
        logging.critical(top_tracks)
        first_top_track = top_tracks["tracks"][0]
        logging.critical(first_top_track)

        artist_seed = first_top_track["album"]["artists"][0]["id"]
        artist_name = first_top_track["album"]["artists"][0]["name"]
        track_name = first_top_track["name"]
        track_id = first_top_track["id"]
        preview_url = first_top_track["preview_url"]
        images = first_top_track["album"]["images"]
        genres = self.get_genre(artist_seed, access_token)

        serialized = SongSerializer(
            {
                "artist_seed": artist_seed,
                "artist_name": artist_name,
                "track_name": track_name,
                "track_id": track_id,
                "preview_url": preview_url,
                "images": images,
                "genres": genres,
            }
        )

        return Response(data=serialized.data)
