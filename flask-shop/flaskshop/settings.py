# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from pathlib import Path

from flask.helpers import get_debug_flag


class DBConfig:
    user = os.getenv("DB_USER", "root")
    passwd = os.getenv("DB_PASSWD", "123456")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", 3306)
    db_name = os.getenv("DB_NAME", "flaskshop")
    db_uri = (
        f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4"
    )



class Config:
    ENV = "dev"
    FLASK_DEBUG = get_debug_flag()
    SECRET_KEY = os.getenv("SECRET_KEY", "thisisashop")

    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI", DBConfig.db_uri)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_QUERY_TIMEOUT = 0.1 
    SQLALCHEMY_RECORD_QUERIES = True

    # Dir
    APP_DIR = Path(__file__).parent  
    PROJECT_ROOT = APP_DIR.parent
    STATIC_DIR = APP_DIR / "static"
    UPLOAD_FOLDER = "upload"
    UPLOAD_DIR = STATIC_DIR / UPLOAD_FOLDER
    DASHBOARD_TEMPLATE_FOLDER = APP_DIR / "templates" / "dashboard"
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/placeholders")

    PURCHASE_URI = os.getenv("PURCHASE_URI", "")

    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = get_debug_flag()
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    MESSAGE_QUOTA = 10

    LANGUAGES = {"en": "English"}

    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = os.getenv("MAIL_PORT", 25)
    MAIL_TLS = os.getenv("MAIL_TLS", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "danylo")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "bookstore")

