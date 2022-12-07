import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request
from microblog.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from microblog.routes import blueprint
from microblog.errors import err
from flask_mail import Mail    # Importojme klasen Mail qe do perdorim si password recovery option.
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from elasticsearch import Elasticsearch


app = Flask(__name__)

app.config.from_object(Config)  # Per te marre konfigurimet per nje klase veprojme dhe keshtu
                                # cf=pp.config['SECRET_KEY']--> po ta kalojme si parameter do na shfaqet stringu
app.register_blueprint(blueprint)
app.register_blueprint(err)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'blueprint.login'   # I themi flaskut se cili eshte view function qe perdorim per tu loguar

mail = Mail(app)        # Krijojme nje instance te klases Mail qe merr si argument instancen app te klases Flask

bootstrap = Bootstrap(app)  # Ne te njejten menyre veprojme dhe me Bootstrap kur duam ta inicializojme

moment = Moment(app)      # Extension that wrap javascript component we must add javascript library to base template

babel = Babel(app)

app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    if app.config['ELASTICSEARCH_URL'] else None


if not app.debug:                   # Kontrollojme nqs jemi ne debug mode
    if app.config['MAIL_SERVER']:   # Kontrollojme mail serverin. Nqs nuk eshte konfiguruar atehere nuk cojme dot email
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@'+ app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'][1], subject="Microblog Failure",
                credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):      # Krijon nje folder logs nqs nuk ekziston
        os.mkdir('logs')
    # Krijon filen dhe dhe parandalon diskun te mbushet plot. Fshin log-et e vjetra dhe mban 10 log-et  fundit
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')     # Sa here starton serveri krijohet nje rresht

@login_manager.user_loader
def load_user(id):
    from microblog.models import User
    return User.query.get(int(id))


# app.app_context().push()

# Kur jemi loguar dhe navigojme nga nje faqe ne tjetren serveri "mban mend" qe ne jemi loguar.
# Kjo implementohet duke shkruar nje flag (user_id) ne session-in e perdoruesit.
# Sesioni i perdoruesit eshte nje hapesire private qe alokohet per cdo klient qe lidhet me aplikacionin.
# Nje extension i flask adreson problemin e te majturit te perdoruesit te loguar.
# Kur nje user ben kerkese per te nje faqe flask-login lexon user_id nga session dhe merr objektin user me ate ID.
# Per kete percaktojme funksionin load_user() ne modulin models ne global scope


@babel.localeselector    # I themi babel-it te zgjedhi gjuhen per nje request te caktuar
def get_locale():
    # Atributi accept_languages i perket objektit request dhe paraqet permbajtjen e language header
    return request.accept_languages.best_match(app.config['LANGUAGES'])

@migrate.configure
def configure_alembic(config):
    # modify config object
    return config


