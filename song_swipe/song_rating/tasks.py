import datetime
import logging

import environ
import requests
from allauth.socialaccount.models import SocialToken

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
