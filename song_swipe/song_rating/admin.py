from django.contrib import admin

from .models import Song, SongStatus

# Register your models here.


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "spotify_id", "author"]
    list_filter = ["author"]
    search_fields = ["name", "spotify_id"]


@admin.register(SongStatus)
class SongStatusAdmin(admin.ModelAdmin):
    list_display = ["id", "song", "user"]
    list_filter = ["song__author"]
    search_fields = ["song_name"]
