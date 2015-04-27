from flask.ext.login import LoginManager

def setup_app(app):
    print "Adding login_manager to app"
    login_manager = LoginManager()
    login_manager.init_app(app)

