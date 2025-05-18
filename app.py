import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Import the db instance from models to avoid multiple SQLAlchemy instances
from models import db

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Import all model files here to ensure they're registered with SQLAlchemy
    import models  # noqa: F401

    # Create all tables
    db.create_all()