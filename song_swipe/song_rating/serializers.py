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

    """
    class Meta:
        model = Song
        fields = ['id', 'spotify_id', 'name', 'author']
    """


class SongListSerializer(serializers.Serializer):
    songs = SongSerializer(many=True)
