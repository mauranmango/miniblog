import os

class Config(object):
   
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-supposed-to-be-secret'
   
   
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
   
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    LANGUAGES = ['sq']
    ADMINS = ['mauran.mango@yahoo.com']           
    POST_PER_PAGE = 5 
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
