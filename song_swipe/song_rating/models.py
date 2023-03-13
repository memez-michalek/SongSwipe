import uuid

from django.db import models

from song_swipe.users.models import User

# from song_swipe.users.models import
# Create your models here.


class Song(models.Model):
    name = models.CharField(max_length=255)
    spotify_id = models.CharField(max_length=40)
    author = models.CharField(max_length=255)


class SongStatus(models.Model):
    STATUS_CHOICES = (("L", "LOVE"), ("H", "HATE"), ("I", "IGNORE"))

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    song = models.OneToOneField(
        Song, on_delete=models.CASCADE, related_name="song_statuses"
    )
    ralation = models.CharField(max_length=1, choices=STATUS_CHOICES)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_statuses"
    )
