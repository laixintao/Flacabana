
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SERCRET_KEY = os.environ.get('SECRET_KEY') or 'this-string-should-hard-#$%^&-to-guess'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLACABANA_MAIL_SUBJECT_PREFIX='[Flacabana]'
    FLACABANA_MAIL_SENDER = 'FLACABANA <Flacabana@example.com>'
    FLACABANA_ADMIN = os.environ.get('FLACABANA_ADMIN')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 87
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
              'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}