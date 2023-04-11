import logging

import requests
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.response import Response

from .mixins import UtilsMixin
from .serializers import SongSerializer
from .tasks import add_song_to_liked, delete_song_from_liked


class SpotifyLogin(SocialLoginView):
    adapter_class = SpotifyOAuth2Adapter
    client_class = OAuth2Client


@method_decorator(csrf_exempt, name="dispatch")
class GetFirstSongView(UtilsMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        """

        IDEAS HOW TO IMPLEMENT ALGORITHM FOR SHOWING USER NEW FRESH SONGS
        1 GET RECENTLY PLAYED ARTIST/TRACK AND GENERES
        2 GET THE MOST RELATED SONG TO RECENTLY PLAYED SONG

        """
        access_token = self.get_users_access_token(request.user)
        response = self.get_users_top_tracks(request.user, access_token)

        if response.status_code != 200:
            return Response(
                "Error Found when trying to suggest tags", status=response.status_code
            )

        serialized = self.package_response(response, access_token)

        response = Response(data=serialized.data)
        return response


@method_decorator(csrf_exempt, name="dispatch")
class LikeSongView(UtilsMixin, viewsets.GenericViewSet):
    # BY DEFAULT LIKE SONG RETURNS NEXT SONG

    def retrieve(self, request, slug, *args, **kwargs):
        spotify_song_id = slug
        access_token = self.get_users_access_token(request.user)

        genres = "%20".join(request.query_params.getlist("genres")[0].split(",")[:5])
        spotify_artist_id = request.query_params.get("spotify_artist_id")

        add_song_to_liked.delay(spotify_song_id, access_token.token)

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

        # RETRIEVE DATA FROM RESPONSE
        first_top_track = recommend_song_response.json()["tracks"][0]
        artist_seed = first_top_track["album"]["artists"][0]["id"]

        song_data = {
            "artist_seed": artist_seed,
            "artist_name": first_top_track["album"]["artists"][0]["name"],
            "track_name": first_top_track["name"],
            "track_id": first_top_track["id"],
            "preview_url": first_top_track["preview_url"],
            "images": first_top_track["album"]["images"],
            "genres": self.get_genre(artist_seed, access_token),
        }

        serialized = SongSerializer(song_data)
        try:
            # Your code here
            return Response(data=serialized.data)
        except Exception as e:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={"message": str(e)}
            )


@method_decorator(csrf_exempt, name="dispatch")
class HateSongView(UtilsMixin, viewsets.GenericViewSet):
    def retrieve(self, request, slug, *args, **kwargs):
        try:
            spotify_song_id = slug
            access_token = self.get_users_access_token(request.user)
            # calls task which deltes song from liked
            delete_song_from_liked.delay(spotify_song_id, access_token.token)

            top_tracks_response = self.get_users_top_tracks(request.user, access_token)
            top_tracks_response.raise_for_status()

            serialized = self.package_response(top_tracks_response, access_token)

            return Response(data=serialized.data)

        except Exception as e:
            logging.exception(e)
            return Response({"error": "Could not block selected track"}, status=500)
