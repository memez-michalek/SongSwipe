from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView


class SpotifyLogin(SocialLoginView):
    adapter_class = SpotifyOAuth2Adapter
