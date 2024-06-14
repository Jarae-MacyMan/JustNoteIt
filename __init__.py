import os

from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__) #creates flask instance
    app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', default='dev')
    )

    if test_config is None:
         # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    return app