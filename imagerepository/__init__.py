import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=b'n\xf7\x81\xb61\xfb.\x97\x19]\xae\x97Q<\xfe,',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        UPLOAD_FOLDER = 'images/'
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    from . import models


    from . import auth, image
    app.register_blueprint(auth.bp)
    app.register_blueprint(image.bp)

    return app