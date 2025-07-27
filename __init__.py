from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = 'ofjhekseoifheo'

    from .home import home
    app.register_blueprint(home,url_prefix='/')

    return app
