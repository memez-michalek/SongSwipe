import datetime
import logging
from contextlib import closing

import environ
import requests
from allauth.socialaccount.models import SocialToken
from celery import shared_task

from config import celery_app

env = environ.Env()


@celery_app.task()
def refresh_auth_tokens():
    logging.info("Refreshing users tokens")

    invalid_tokens = SocialToken.objects.filter(expires_at__lt=datetime.datetime.now())

    client_id = (env("SPOTIFY_CLIENT_ID"),)
    client_secret = (env("SPOTIFY_CLIENT_SECRET"),)

    for token in invalid_tokens:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": token.token_secret,
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        SocialToken.objects.filter(id=token.id).update(
            token=response.json()["access_token"],
            expires_at=datetime.datetime.now() + datetime.timedelta(hours=1),
        )


@shared_task
def delete_song_from_liked(spotify_song_id, access_token):
    url = f"https://api.spotify.com/v1/me/tracks?ids={spotify_song_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {access_token}",
    }
    with closing(requests.delete(url, headers=headers)) as response:
        if response.status_code != 200:
            logging.info("Error when deleting song")
            # return False
        # return True


@shared_task
def add_song_to_liked(spotify_song_id, access_token):
    url = f"https://api.spotify.com/v1/me/tracks?ids={spotify_song_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {access_token}",
    }
    with closing(requests.put(url, headers=headers)) as response:
        if response.status_code != 200:
            logging.info("Error when deleting song")
