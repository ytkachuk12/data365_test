"""Test task: flask simple web service for social network backend

For run application using the flask command in the terminal
    export FLASK_APP=flask_app
    export FLASK_ENV=development
    flask init-db
    flask run
    """

import os

from flask import Flask


def create_app(test_config=None):
    """It's application factory
    Create and configure an instance of the Flask application."""
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the flask_app folder
        DATABASE=os.path.join(app.instance_path, 'flask_app.sqlite'),
    )

    # load the config, if it exists, when not testing
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from flask_app import db
    db.init_app(app)

    # apply the blueprints to the app
    from flask_app import blog
    # register blueprint
    app.register_blueprint(blog.bp)

    return app
