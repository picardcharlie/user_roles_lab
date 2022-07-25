import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = "hello_world"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "test.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SERVER_NAME = "http://localhost:5000/"

    #flask-mail settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    #local mail settings
    ZOMBO_ADMIN = os.environ.get("ZOMBO_ADMIN")
    ZOMBO_MAIL_SUBJECT_PREFIX = "ZOMBO - "
    ZOMBO_MAIL_SENDER = f"ZOMBO admin {ZOMBO_ADMIN}"

    @staticmethod
    def init_app(app):
        pass

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TESTING_URI") or "sqlite:///" + os.path.join(basedir, "data-test.sqlite")

config = {"default": Config, "testing": TestingConfig}