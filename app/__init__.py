from flask import Flask
from flask_socketio import SocketIO
from flask_clacks import Clacks  # rip terry pratchett
from werkzeug.middleware.proxy_fix import ProxyFix
import os

socketio = SocketIO()


def create_app(debug=False):
    app = Flask(__name__, static_folder='./static')
    Clacks(app)
    app.debug = debug
    app.config['SECRET_KEY'] = os.environ("FLASK_SECRETKEY")
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app,
                      cors_allowed_origins=["*"],
                      async_mode='eventlet',
                      logger=True,
                      engineio_logger=True,
                      cookie='io',
                      cookie_samesite='None',
                      cookie_secure=True)

    return app
