from frasco import Feature, action, flash, url_for, hook, lazy_translate
from frasco_users import current_user
from .blueprint import create_blueprint


class GithubFeature(Feature):
    name = "github"
    requires = ["users"]
    blueprints = [create_blueprint]
    defaults = {"use_username": True,
                "use_email": True,
                "scope": 'user:email',
                "user_denied_login_message": lazy_translate("Login via Github was denied")}

    def init_app(self, app):
        self.app = app
        self.api = app.features.users.create_oauth_app("github",
            base_url='https://api.github.com/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            consumer_key=self.options["consumer_key"],
            consumer_secret=self.options["consumer_secret"],
            request_token_params={'scope': self.options['scope']},
            login_view="github_login.login")

        @self.api.tokengetter
        def token_getter():
            if not current_user.is_authenticated() or not current_user.github_access_token:
                return
            return (current_user.github_access_token, "")

        self.model = app.features.models.ensure_model(app.features.users.model,
            github_access_token=str,
            github_username=str,
            github_id=dict(type=str, index=True),
            github_email=str)