import os
from dotenv import load_dotenv

# __file__ path to config . py
# by applying os.path.dirname we remove the path of the file from the abs path.
basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))#

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
         'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    POSTS_PER_PILL = 6

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_SES_SENDER = 'contact@progressoneledilizia.com'
    AWS_SES_CHARSET = 'UTF-8'
    AWS_REGION = 'eu-central-1'
    AWS_BUCKET_NAME = 'progressoneledilizia'
    
    ADMINS = ['dan@progressoneledilizia.com']

    IMAGE_DIR = 'static/assets/images/projects/'
    GENERAL_IMAGES_PATH = ''
    
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')
