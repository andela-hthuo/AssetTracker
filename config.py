import os


class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = 'kSec2e+iZlgjjKChKdUY5Iw0kurzjsGX'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.mailgun.org'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
    GOOGLE_WEB_CLIENT_ID = os.environ['GOOGLE_WEB_CLIENT_ID']
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'uploads')


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    BOOTSTRAP_SERVE_LOCAL = True


class TestingConfig(Config):
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
