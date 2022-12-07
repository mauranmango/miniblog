import os
#import psycopg2

class Config(object):
    # Nqs ka nje environment variable SECRET_KEY merr nga ajo variabel ne te kundert merr stringun
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this-is-supposed-to-be-secret'
    # Per ti thene flaskut se ku ndodhet databaza ka nevoje per variabel konfigurimi
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://postgres:Mauran123@localhost:5432/microblog"
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')  #'postgresql://postgres:Mauran123@localhost:5432/micro'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Si fillim konfigurojme email server-in
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    LANGUAGES = ['sq']
    ADMINS = ['mauran.mango@yahoo.com', 'aurora.ostrovica@gmail.com']            # Do konfigurojme adresat e administratorit qe do marri emailet
    POST_PER_PAGE = 5  # Do shtojme nje konfigurim se sa postime per faqe duam te kemi
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
