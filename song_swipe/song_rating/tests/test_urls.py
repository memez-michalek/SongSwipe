from django.test.utils import TestCase
from django.urls import reverse


class TestSongRatingUrls(TestCase):
    def test_song_url(self):
        self.assertEqual(reverse("song_rating:song"), "/api/song/")
