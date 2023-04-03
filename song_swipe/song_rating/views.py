import json
import logging
import random

import requests
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import status, viewsets
from rest_framework.response import Response

# from .adapters import MySocialAccountAdapter
from song_swipe.users.models import User

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

    def get_users_spotify_id(self, access_token):
        response = requests.get(
            "https://api.spotify.com/v1/me",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        if response.status_code != 200:
            raise ValueError("responses status code is different than 200")

        profile = response.json()
        return profile["id"]

    def add_song_to_playlist(self, access_token, playlist_id, track_uri):
        # check if song is already in playlist

        response = requests.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        playlist_tracks = response.json()["items"]

        # Extract track URIs
        track_uris = [track["track"]["uri"] for track in playlist_tracks]

        if track_uri in track_uris:
            return False

        response = requests.post(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
            json={"uris": [track_uri]},
        )

        response.raise_for_status()

        return True

    def package_response(self, response, access_token):
        top_tracks = response.json()
        try:
            first_track = top_tracks["items"][random.randint(0, 9)]
        except KeyError:
            first_track = top_tracks["tracks"][0]

        artist_seed = first_track["album"]["artists"][0]["id"]
        artist_name = first_track["album"]["artists"][0]["name"]
        track_name = first_track["name"]
        track_id = first_track["id"]
        preview_url = first_track["preview_url"]
        images = first_track["album"]["images"]
        logging.critical(images)

        genres = self.get_genre(artist_seed, access_token)

        logging.critical(genres)
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
        logging.critical(serialized.data)

        return serialized


class SpotifyLogin(SocialLoginView):
    adapter_class = SpotifyOAuth2Adapter
    client_class = OAuth2Client


class GetFirstSongView(UtilsMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        """
        IDEAS HOW TO IMPLEMENT ALGORITHM FOR SHOWING USER NEW FRESH SONGS
        1 GET RECENTLY PLAYED ARTIST/TRACK AND GENERES
        2 GET THE MOST RELATED SONG TO RECENTLY PLAYED SONG

        """
        user = User.objects.get(id=request.user.id)
        access_token = SocialToken.objects.get(
            app__provider="spotify", account__user=request.user
        )

        if (
            request.user.users_playlist_id is None
            or request.user.users_playlist_id == ""
        ):
            user_id = self.get_users_spotify_id(access_token)
            response = requests.post(
                f"https://api.spotify.com/v1/users/{user_id}/playlists",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {access_token}",
                },
                data=json.dumps(
                    {
                        "name": "song_swipe_playlist",
                        "description": "playlist created by songswipe",
                        "public": True,
                    }
                ),
            )
            if response.status_code != 201:
                return Response(
                    "could not create playlist", status=status.HTTP_404_NOT_FOUND
                )

            user.users_playlist_id = response.json()["id"]
            user.save()

        response = requests.get(
            "https://api.spotify.com/v1/me/top/tracks",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        # logging.critical(response.json())
        if response.status_code != 200:
            return Response("Error Found", status=response.status_code)

        serialized = self.package_response(response, access_token)

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
        spotify_playlist_id = request.user.users_playlist_id

        response = requests.put(
            f"https://api.spotify.com/v1/me/tracks?ids={spotify_song_id}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )

        if response.status_code != 200:
            return Response("Could not add selected track", status=response.status_code)

        url = (
            "https://api.spotify.com/v1/recommendations"
            "?limit=10"
            "&market=PL"
            f"&seed_artists={spotify_artist_id}"
            f"&seed_genres={genres}"
            f"&seed_tracks={spotify_song_id}"
        )

        recommended_tracks_response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )

        if recommended_tracks_response.status_code != 200:
            return Response(
                "Could not recommend next track",
                status=recommended_tracks_response.status_code,
            )

        track_uri = f"spotify:track:{spotify_song_id}"
        # ADD SONG TO PLAYLIST
        # logging.critical(f"playlist id {spotify_playlist_id}")
        if not self.add_song_to_playlist(access_token, spotify_playlist_id, track_uri):
            logging.info("Could not add song to playlist")
            """
            return Response(
                data="Could not add song to playlist",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            """

        serialized = self.package_response(recommended_tracks_response, access_token)
        return Response(data=serialized.data)


# ONLY DELETES SONG FROM LIBRARY BECAUSE SPOTIFY HIDING VIA API IS IMPOSSIBLE
class HateSongView(UtilsMixin, viewsets.GenericViewSet):
    def retrieve(self, request, slug, *args, **kwargs):
        # spotify_song_id = self.kwargs.get("spotify_song_id")
        spotify_song_id = slug
        access_token = SocialToken.objects.get(
            app__provider="spotify", account__user=request.user
        )
        # genres = request.query_params.get("genres")

        response = requests.delete(
            f"https://api.spotify.com/v1/me/tracks?ids={spotify_song_id}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )

        if response.status_code != 200:
            return Response(
                "Could not block selected track", status=response.status_code
            )

        response = requests.get(
            "https://api.spotify.com/v1/me/top/tracks",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        if response.status_code != 200:
            return Response("Error Found", status=response.status_code)

        serialized = self.package_response(response, access_token)
        return Response(data=serialized.data)
