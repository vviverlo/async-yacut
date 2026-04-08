import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from . import error_handlers, views, api_views
from .exceptions import ShortLinkAPIError

app.register_error_handler(
    ShortLinkAPIError,
    error_handlers.short_link_api_error,
)
app.register_error_handler(404, error_handlers.page_not_found)
app.register_error_handler(500, error_handlers.internal_server_error)

with app.app_context():
    db.create_all()
