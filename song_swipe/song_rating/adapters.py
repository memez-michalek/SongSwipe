from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, **kwargs):
        # NOTE: Avoid loading models at top due to registry boot...
        # 1 added line here
        from allauth.socialaccount import app_settings
        from allauth.socialaccount.models import SocialApp

        config = app_settings.PROVIDERS.get(provider, {}).get("APP")
        app = SocialApp.objects.get_or_create(provider=provider)[0]
        app.client_id = config["client_id"]
        app.secret = config["secret"]
        app.key = config.get("key", "")
        return app
