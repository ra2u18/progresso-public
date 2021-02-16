import os
import logging
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail

from logging.handlers import SMTPHandler, RotatingFileHandler

from config import Config

from redis import Redis
import rq

# AWS SES library
import boto3

# Extentions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()

# When a page requires login, this setting is how the LoginManager knows
# where to send the user for logging in.
login_manager.login_view = 'auth.login'
login_manager.login_message_category= 'info'

# Setting configurations for the application -
# for different types of configurations.
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    # Initialize extensions with the application instance.
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('progresso-tasks', connection = app.redis)

    print(app.config['SECRET_KEY'],app.config['AWS_ACCESS_KEY_ID'], app.config['AWS_SECRET_ACCESS_KEY'])

    app.ses_client = boto3.client(
        'ses',
        region_name=app.config['AWS_REGION'],
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
    )

    app.s3_client = boto3.client('s3', region_name=app.config['AWS_REGION'])

    # Register blueprints.
    from app.auth import bp as auth
    from app.portfolio import bp as portfolio
    from app.main import bp as main

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(portfolio)
    app.register_blueprint(main)

    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Progresso Nel Edilizia Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
    app.logger.setLevel(logging.INFO)
    app.logger.info('Progresso nel Edilizia startup')

    return app



