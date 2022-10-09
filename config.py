import os

basedir = os.path.abspath(os.path.dirname(__file__))

class DevelopmentConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'local.db')