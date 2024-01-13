import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLITE_DB_NAME = "app.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, SQLITE_DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = os.urandom(12)

