from flask import Flask
#from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
# app.config.from_object(Config)

# https://github.com/Azure-Samples/msdocs-flask-postgresql-sample-app
# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('config.dev')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('config.prod')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)


db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
