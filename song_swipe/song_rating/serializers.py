from rest_framework import serializers


class SongSerializer(serializers.Serializer):
    artist_seed = serializers.CharField(max_length=22)
    artist_name = serializers.CharField(max_length=128)
    track_name = serializers.CharField(max_length=256)
    track_id = serializers.CharField(max_length=22)
    preview_url = serializers.URLField()
    images = serializers.ListField(
        child=serializers.URLField(),
    )
    genres = serializers.ListField(
        child=serializers.CharField(),
    )

    def to_representation(self, instance):
        return {
            "artist_seed": instance["artist_seed"],
            "artist_name": instance["artist_name"],
            "track_name": instance["track_name"],
            "track_id": instance["track_id"],
            "preview_url": instance["preview_url"],
            "images": instance["images"],
            "genres": instance["genres"],
        }
