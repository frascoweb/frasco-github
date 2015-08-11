from frasco import Feature, action, flash, url_for, hook, lazy_translate, Blueprint, redirect, request
from frasco_users import current_user


def create_blueprint(app):
    bp = Blueprint("github_login", __name__)

    feature = app.features.github
    users = app.features.users

    @bp.route('/login/github')
    def login():
        callback_url = url_for('.callback', next=request.args.get('next'), _external=True)
        kwargs = {}
        if 'scope' in request.args:
            kwargs['scope'] = request.args['scope']
        return feature.api.authorize(callback=callback_url, **kwargs)

    @bp.route('/login/github/callback')
    def callback():
        resp = feature.api.authorized_response()
        if resp is None:
            flash(feature.options["user_denied_login_message"], "error")
            return redirect(url_for("users.login"))

        me = feature.api.get('user', token=[resp['access_token']])
        attrs = {"github_access_token": resp['access_token'],
                 "github_username": me.data['login'],
                 "github_id": str(me.data['id']),
                 "github_email": me.data.get('email'),
                 "github_scope": resp['scope']}
        defaults = {}
        if feature.options["use_email"] and 'email' in me.data:
            defaults[users.options["email_column"]] = me.data['email']
        if feature.options["use_username"] and users.options['email_column'] != users.options['username_column']:
            defaults[users.options["username_column"]] = me.data['login']

        return users.oauth_login("github", "github_id", str(me.data['id']), attrs, defaults)

    return bp


class GithubFeature(Feature):
    name = "github"
    requires = ["users"]
    blueprints = [create_blueprint]
    defaults = {"use_username": True,
                "use_email": True,
                "scope": None,
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
            github_email=str,
            github_scope=str)

    def has_scope(self, *scopes):
        if current_user.github_scope:
            available_scopes = current_user.github_scope.split(',')
            for scope in scopes:
                if scope not in available_scopes:
                    return False
            return True
        return False

    def update_scope(self, *scopes):
        if current_user.github_scope:
            current_scopes = set(current_user.github_scope.split(','))
            current_scopes.update(scopes)
            return ",".join(current_scopes)
        return ",".join(scopes)