import os
from datetime import timedelta

from flask.cli import load_dotenv

load_dotenv()


class Config:
    # Безопасность
    SECRET_KEY = os.getenv("SECRET_KEY")
    WTF_CSRF_ENABLED = bool(os.getenv("WTF_CSRF_ENABLED"))

    # Настройки сессии
    SESSION_TYPE = os.getenv("SESSION_TYPE")
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Настройки почтового сервера
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = bool(os.getenv("MAIL_USE_TLS"))
    # MAIL_USE_SSL = bool(os.getenv("MAIL_USE_SSL")) Production
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # Настройки базы данных
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = bool(os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS"))

    # Настройки YandexGPT
    YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")
    YC_API_KEY = os.getenv("YC_API_KEY")
