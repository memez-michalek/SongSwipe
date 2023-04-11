import logging
import random

import requests
from allauth.socialaccount.models import SocialToken
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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

        first_track = top_tracks["items"][random.randint(0, 49)]
        serialized = self.serialize_tracks(first_track, access_token)
        return serialized

    def get_users_top_tracks(self, user, access_token):
        top_tracks = cache.get(f"{user}-top-tracks")
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
                "https://api.spotify.com/v1/me/top/tracks?limit=50",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {access_token}",
                },
            )
            logging.critical(response)
            # logging.critical(response.json())
            if response.status_code != 200:
                return logging.critical(
                    "Error Found when trying to suggest tags",
                    status=response.status_code,
                )

            cache.set(f"{user}-top-tracks", response, timeout=86400)
            top_tracks = response

        return top_tracks

    def get_users_access_token(self, user):
        access_token = cache.get(f"{user}-access-token")
        if access_token is None:
            access_token = SocialToken.objects.get(
                app__provider="spotify", account__user=user
            )

            cache.set(f"{user}-access-token", access_token, timeout=600)

        return access_token

    """
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

    """
