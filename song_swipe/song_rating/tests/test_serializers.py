import pytest

from song_swipe.song_rating.serializers import SongSerializer


@pytest.fixture()
def song_data():
    return {
        "artist_seed": "1234",
        "artist_name": "John Doe",
        "track_name": "Best Song Ever",
        "track_id": "5678",
        "preview_url": "https://example.com",
        "images": ["https://example.com/image1.png", "https://example.com/image2.png"],
        "genres": ["Rock", "Pop"],
    }


@pytest.mark.parametrize(
    "data, expected", [(song_data(), True), ({**song_data(), "artist_name": ""}, False)]
)
def test_song_serializer_valid(data, expected):
    serializer = SongSerializer(data=data)
    assert serializer.is_valid() == expected


@pytest.mark.parametrize(
    "data, expected_errors",
    [
        (
            {**song_data(), "artist_name": ""},
            {"artist_name": ["This field may not be blank."]},
        ),
        (
            {**song_data(), "artist_name": "a" * 129},
            {"artist_name": ["Ensure this field has no more than 128 characters."]},
        ),
        (
            {**song_data(), "preview_url": "not a url"},
            {"preview_url": ["Enter a valid URL."]},
        ),
    ],
)
def test_song_serializer_errors(data, expected_errors):
    serializer = SongSerializer(data=data)
    assert not serializer.is_valid()
    assert serializer.errors == expected_errors


def test_song_serializer_save(song_data):
    serializer = SongSerializer(data=song_data)
    assert serializer.is_valid()
    song = serializer.save()
    assert song.id is not None
    assert song.spotify_id == song_data["track_id"]
    assert song.name == song_data["track_name"]
    assert song.author == song_data["artist_name"]


def test_song_serializer_update(song_data):
    serializer = SongSerializer(data=song_data)
    assert serializer.is_valid()
    song = serializer.save()

    updated_data = {
        "artist_seed": "1234",
        "artist_name": "Jane Doe",
        "track_name": "Best Song Ever",
        "track_id": "5678",
        "preview_url": "https://example.com",
        "images": ["https://example.com/image1.png", "https://example.com/image2.png"],
        "genres": ["Rock", "Pop"],
    }

    updated_serializer = SongSerializer(song, data=updated_data)
    assert updated_serializer.is_valid()
    updated_song = updated_serializer.save()
    assert updated_song.id == song.id
    assert updated_song.spotify_id == song_data["track_id"]
    assert updated_song.name == song_data["track_name"]
    assert updated_song.author == updated_data["artist_name"]
