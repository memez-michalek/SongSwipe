import json
import logging
import random

import requests
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import SongSerializer


class UtilsMixin:
    def get_genre(self, artist_seed, access_token):
        artist_genres = cache.get(artist_seed)
        logging.critical(f"artist genres before request {artist_genres}")
        if artist_genres is None:
            retry_strategy = Retry(
                total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)

            response = http.get(
                f"https://api.spotify.com/v1/artists/{artist_seed}",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {access_token}",
                },
            )
            logging.critical(response)
            artist_genres = response.json()["genres"]
            cache.set(artist_seed, response.json()["genres"], timeout=86400)

        # ITS GOOFY BECAUSE SINGLE SONG REQUEST WORKS BUT
        # LIKE SONG DOES NOT

        # if response.status_code != 200:
        #    return Response("could not gather genre", status=status.HTTP_404_NOT_FOUND)
        logging.critical(f"artist gathered genres {artist_genres}")
        return artist_genres

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

    def serialize_tracks(self, track, access_token):
        artist_seed = track["album"]["artists"][0]["id"]
        artist_name = track["album"]["artists"][0]["name"]
        track_name = track["name"]
        track_id = track["id"]
        preview_url = track["preview_url"]
        images = track["album"]["images"]
        logging.critical(images)
        logging.critical(f"artist seed {artist_seed}")

        genres = self.get_genre(artist_seed, access_token)
        logging.critical("genres")
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
        logging.critical(f"serialized track{serialized.data}")
        return serialized

    def package_response(self, response, access_token):
        top_tracks = response.json()

        try:
            first_track = top_tracks["items"][random.randint(0, 9)]
            serialized = self.serialize_tracks(first_track, access_token)
            return serialized

        # TURNS OUT EXCEPTION WORKS JUST FINE
        except KeyError:
            tracks = top_tracks["tracks"][0]

            serialized = self.serialize_tracks(tracks, access_token)
            return serialized

    def get_users_top_tracks(self, user, access_token):
        top_tracks = cache.get(user)
        if top_tracks is None:
            retry_strategy = Retry(
                total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)

            # Compute the data and store it in the cache
            response = http.get(
                "https://api.spotify.com/v1/me/top/tracks",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {access_token}",
                },
            )
            # logging.critical(response.json())
            if response.status_code != 200:
                return logging.critical(
                    "Error Found when trying to suggest tags",
                    status=response.status_code,
                )

            cache.set(user, response, timeout=3600)
            top_tracks = response

        return top_tracks

    def get_users_recommendations(
        self, user, access_token, spotify_artist_id, genres, spotify_song_id
    ):
        recommendations = cache.get(f"recommendations-{user}")
        if recommendations is None or len(recommendations) == 0:
            retry_strategy = Retry(
                total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)

            url = (
                "https://api.spotify.com/v1/recommendations"
                "&market=PL"
                f"&seed_artists={spotify_artist_id}"
                f"&seed_genres={genres}"
                f"&seed_tracks={spotify_song_id}"
            )

            recommendations = http.get(
                url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
            )
            logging.critical(f"returned recommendations{dir(recommendations)}")
            logging.critical(recommendations.json())
            recommendations = recommendations.json()["tracks"][0]
            cache.set(f"recommendations-{user}", recommendations, timeout=3600)

        recommended_track = recommendations.pop(0)
        cache.set(f"recommendations-{user}", recommendations, timeout=3600)
        return recommended_track


class SpotifyLogin(SocialLoginView):
    adapter_class = SpotifyOAuth2Adapter
    client_class = OAuth2Client


@method_decorator(csrf_exempt, name="dispatch")
class GetFirstSongView(UtilsMixin, viewsets.GenericViewSet):
    """def options(self, request, *args, **kwargs):
    allowed_methods = ['GET', 'OPTIONS']  # add OPTIONS to the list of allowed methods
    response = Response()
    response['Allow'] = ', '.join(allowed_methods)
    return response
    """

    def list(self, request, *args, **kwargs):
        """

        IDEAS HOW TO IMPLEMENT ALGORITHM FOR SHOWING USER NEW FRESH SONGS
        1 GET RECENTLY PLAYED ARTIST/TRACK AND GENERES
        2 GET THE MOST RELATED SONG TO RECENTLY PLAYED SONG

        """

        access_token = SocialToken.objects.get(
            app__provider="spotify", account__user=request.user
        )
        user = access_token.account.user

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

        response = self.get_users_top_tracks(request.user, access_token)
        """

        response = requests.get(
            "https://api.spotify.com/v1/me/top/tracks",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        """
        # logging.critical(response.json())
        if response.status_code != 200:
            return Response(
                "Error Found when trying to suggest tags", status=response.status_code
            )

        serialized = self.package_response(response, access_token)

        response = Response(data=serialized.data)
        # response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        # response["Access-Control-Allow-Credentials"] = "true"
        return response


'''
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
        logging.critical(genres)
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


        formated_genres = "".join(genres)
        formated_genres.replace(",", " ")
        url = (
            "https://api.spotify.com/v1/recommendations"
            "?limit=10"
            "&market=PL"
            f"&seed_artists={spotify_artist_id}"
            f"&seed_genres={formated_genres}"
            f"&seed_tracks={spotify_song_id}"
        )
        logging.critical(f"request url {url}")
        recommended_tracks_response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )
        logging.critical(recommended_tracks_response)
        #logging.critical(f"next recommended track{recommended_tracks_response.json()}")
        if recommended_tracks_response.status_code != 200:
            return Response(
                "Could not recommend next track",
                status=recommended_tracks_response.status_code,
            )

        track_uri = f"spotify:track:{spotify_song_id}"
        # ADD SONG TO PLAYLIST
        # logging.critical(f"playlist id {spotify_playlist_id}")
        logging.critical(track_uri)
        if not self.add_song_to_playlist(access_token, spotify_playlist_id, track_uri):
            logging.info("Could not add song to playlist")
            """
            return Response(
                data="Could not add song to playlist",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            """

        #serialized = self.package_response(recommended_tracks_response, access_token)
        tracks = recommended_tracks_response.json()["tracks"][0]
        logging.critical(f"TRACKS ANALISIS {tracks}")

        serialized = self.serialize_tracks(tracks, access_token)
        logging.critical(f"serialized item {serialized}")



        logging.critical(f"serialized before returned {serialized.data}")
        return Response(data=serialized.data)
'''


@method_decorator(csrf_exempt, name="dispatch")
class LikeSongView(UtilsMixin, viewsets.GenericViewSet):
    # BY DEFAULT LIKE/HATE/IGNORE SONG RETURNS NEXT SONG AND STATUS IF
    # SONG HAS BEEN ADDED SUCCESSFULY

    def retrieve(self, request, slug, *args, **kwargs):
        # spotify_song_id = self.kwargs.get("spotify_song_id")
        spotify_song_id = slug
        access_token = SocialToken.objects.get(
            app__provider="spotify", account__user=request.user
        )
        genres = "%20".join(request.query_params.getlist("genres")[0].split(",")[:5])
        spotify_artist_id = request.query_params.get("spotify_artist_id")

        response = requests.put(
            f"https://api.spotify.com/v1/me/tracks?ids={spotify_song_id}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        logging.critical(f"song added to liked response{response}")
        if response.status_code != 200:
            logging.critical(response.json())
            return Response("Could not add selected track")

        logging.critical(genres)
        url = (
            "https://api.spotify.com/v1/recommendations"
            "?limit=10"
            "&market=PL"
            f"&seed_artists={spotify_artist_id}"
            f"&seed_genres={genres}"
            f"&seed_tracks={spotify_song_id}"
        )

        recommend_song_response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )
        logging.critical(f"recommended song response{recommend_song_response.json()}")
        """
         = self.get_users_recommendations(
            request.user,
            access_token,
            spotify_artist_id,
            genres,
            spotify_song_id,
        )

        """

        # RETRIEVE DATA FROM RESPONSE
        first_top_track = recommend_song_response.json()["tracks"][0]

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
        # logging.critical(f"serialized response {serialized}")
        return Response(data=serialized.data)


@method_decorator(csrf_exempt, name="dispatch")
# ONLY DELETES SONG FROM LIBRARY BECAUSE SPOTIFY HIDING VIA API IS IMPOSSIBLE
class HateSongView(UtilsMixin, viewsets.GenericViewSet):
    def retrieve(self, request, slug, *args, **kwargs):
        # spotify_song_id = self.kwargs.get("spotify_song_id")
        spotify_song_id = slug
        access_token = SocialToken.objects.get(
            app__provider="spotify", account__user=request.user
        )

        # genres = request.query_params.get("genres")
        logging.critical("hate song view")
        delete_song_response = requests.delete(
            f"https://api.spotify.com/v1/me/tracks?ids={spotify_song_id}",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        logging.critical(
            f"DELETE response status code: {delete_song_response.status_code}"
        )
        logging.critical(f"DELETE response content: {delete_song_response.content}")

        if delete_song_response.status_code != 200:
            return Response(
                "Could not block selected track",
                status=delete_song_response.status_code,
            )
        """
        top_tracks_response = requests.get(
            "https://api.spotify.com/v1/me/top/tracks",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {access_token}",
            },
        )
        """
        top_tracks_response = self.get_users_top_tracks(request.user, access_token)

        if top_tracks_response.status_code != 200:
            return Response("Error Found", status=top_tracks_response.status_code)

        logging.critical(f"top tracks response before packaging {top_tracks_response}")
        serialized = self.package_response(top_tracks_response, access_token)
        logging.critical(f"hate song after serialization {serialized.data}")

        response = Response(data=serialized.data)
        # response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        # response["Access-Control-Allow-Credentials"] = "true"
        return response
