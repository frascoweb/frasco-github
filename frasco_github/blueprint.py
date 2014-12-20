from frasco import Blueprint, redirect, url_for, request, flash


def create_blueprint(app):
    bp = Blueprint("github_login", __name__)

    feature = app.features.github
    users = app.features.users

    @bp.route('/login/github')
    def login():
        callback_url = url_for('.callback', next=request.args.get('next'), _external=True)
        return feature.github.authorize(callback=callback_url)

    @bp.route('/login/github/callback')
    def callback():
        resp = feature.github.authorized_response()
        if resp is None:
            flash(feature.options["user_denied_login_message"], "error")
            return redirect(url_for("users.login"))

        me = feature.github.get('user', token=[resp['access_token']])
        attrs = {"github_access_token": resp['access_token'],
                 "github_username": me.data['login'],
                 "github_id": str(me.data['id']),
                 "github_email": me.data['email']}
        defaults = {}
        if feature.options["use_email"]:
            defaults[users.options["email_column"]] = me.data['email']
        if feature.options["use_username"]:
            defaults[users.options["username_column"]] = me.data['login']

        return users.oauth_login("github", "github_id", str(me.data['id']), attrs, defaults)

    return bp