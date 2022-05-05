# https://flask.palletsprojects.com/en/2.1.x/tutorial/factory/
# This file serves double duty:
# it will contain the application factory,
# and it tells Python that the AmateurBank directory should be treated as a package.

import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bank.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    # return app

    # Import and call this function from the factory.
    from . import db
    db.init_app(app)
    # Import and register the blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    from . import account
    app.register_blueprint(account.bp)
    app.add_url_rule('/', endpoint='index')
    return app


"""
$ flask init-db 
Initialized the database.
There will now be a bank.sqlite file in the instance folder in your project.
"""
