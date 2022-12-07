from flask_login import UserMixin   # Base class per modelin qe ben implementimin e duhur per atributet qe do shtohen
from microblog import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time
from hashlib import md5
import jwt
from microblog.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


# Kjo tabele ndihmese eshte ajo qe na duhet per te shprehur many-to-many relationship
followers = db.Table(
    'followers',
     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

# Do krijojme klase per cdo entitet qe do ruajme ne databaze.
# Do trashegoje nga db.Model e cila eshte klasa baze per te gjitha modelet qe sigurohen nga flask sqlalchemy
class User(UserMixin, db.Model):  # UserMixin e ben modelin User te perputhshem me flask-login
    query: db.Query  # Type hint here | Kjo eshte menyra se si te behet autocomplete query
    # Do perdorim variablat e klases per te percaktuar atributet e kesaj databaze
    id = db.Column(db.Integer, primary_key=True)
    # Si do i kerkojme user-at ne kete tabele? Relational Databases bejne kerkime efektive nqs nje nga atributet qe po kerkon eshte indeksuar.
    # Prandaj percaktojme index=True. Gjithashtu username/email duhet te jene unike
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))      # Per shkak se po shtojme 2 fieldo do gjenerojme nje DB migration
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())  # Hera e fundit qe ka pare profilin

    # SQLAlchemy e ben me te lehte kerkimin e nje autori per nje post dhe anasjelltas postimet per nje autor
    # Kur kemi one to many relationship ky field krijohet nga "one" side qe eshte nje menyre per te aksesuar "many"
    posts = db.relationship('Post', backref='author', lazy="dynamic")     # THIS IS A HIGHER LEVEL CONSTRUCT THAT EXISTS IN THE MODEL SPACE NOT IN THE DATABASE
    # Nqs do kemi u = User(id=1) atehere u.posts do na ktheje te gjitha postimet te shkruar nga ky user
    # 'Post' eshte modeli qe perfaqeson anen 'many' ne kete relationship. KY ATRIBUT PERFAQESON NJE QUERY QE GJENEROHET NGA SQLALCHEMY. NE TE NJEJTEN MENYRE SHTOHET 'author' TE MODELI POST
    # backref do shtojme atributin author te modeli Post. lazy='dynamic' e ben qe posts te jete query dhe jo nje liste
    # Pra nqs: mauran = User(id=1, username='mauran', email='mauran.mango@yahoo.com') atehere
    #          post = Post(id=2, body="askdf", author=mauran) ---> shton atributin author = objektin User


    # users = User.query.order_by(User.username.asc()).all()
    # for u in users:
    #     db.session.delete(u)
    #     db.session.commit()       -----> keshtu fshijme rekordet nga databaza e renditura ne rendin rrites



    # Duke e pare nga ana e Follower lidhja do jete keshtu: Do shfaqi listen e atyre qe ndjek.
    # KWArgumenti secondary na tregon se cila eshte tabela ndihmese
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')


    def __repr__(self):  # Per ta bere kete klase debugging friendly percaktojme kete metode qe shfaq klasen ne konsole.
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Do inkorporojme avatarin te modeli user.
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://gravatar.com/avatar/{digest}?d=identicon&s={size}"  # Kjo do jete adresa e imazhit te avatarit

    def follow(self, user):
        if not self.is_following(user):  # Do shmangi dublikimet e ndjekesve
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):  # Ketu do jete e kunderta. Pra nqs e ndjek atehere mund ta heqi si follower
            self.followed.remove(user)

    def is_following(self, user):  # Do kontrolloje nqs ka nje relationship ne DB me kete user.
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0  # Metoda filter merr nje expression

    def followed_posts(self):   # Do shfaqi postimet e userave qe ndjekim dhe postimet tona sipas postimit me te fundit
        # I ruajme postimet ne nje variabel dhe me pas aplikojme union
        followed = Post.query.join(followers, followers.c.followed_id == Post.user_id).filter(
            followers.c.follower_id == self.id)
        return followed.union(self.posts).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        from microblog import app
        # Dictionaryn e enkripton me algoritmin 256 dhe me key qe kemi percaktuar qe duhet te jete shume sekret
        # Nje feature tjeter qe kane token eshte qe kane date skadence
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        from microblog import app
        try:
            # Ne kete menyre dekodojme informacionin qe koduam. Mund te kemi shume algoritme qe suportojme prandaj e percaktojme si liste
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']

        except:
            return                         # This is going to stop a partial recovery
        return User.query.get(id)          # Nqs token do jete i sakte atehere do na japi nje id te vlefshme dhe si rrjedhoje kthejme ate User


# Ky objekt ekziston vetem si python object dhe nuk ekziston ne databaze.
# Prandaj perdorim migration per te kaluar kete tabele ne databaze
# Hapat qe ndiqen:
# 1. flask db init ---> krijon folderin migration qe do mbaje migrimet e databazes dhe ndryshimet
# 2. flask db migrate -m "user table" -> krijon migrimin e pare i cili merr si argument nje mesazh. Krijon nje script brenda folderit migration
# 3. flask db upgrade --> scripti qe krijohet ka dy funksione upgrade/downgrade dhe ne kete rast ekzekutohet upgrade
# *** Qe te krijohet tabela ne databaze importojme modelet te file env.py qe ndodhet te folderi migrations



class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    query: db.Query  # Type hint here | Kjo eshte menyra se si te behet autocomplete query
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # merr kohen aktuale nqs eshte bosh

    # Na duhet gjithashtu se kush eshte autori i ketij posti dhe per kete na duhet ralationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # What kind of entity is it referencing
    language = db.Column(db.String(5))

    def __repr__(self):
        return f"<Post {self.body}"
    # Do shtojme dicka qe nuk eshte pjese e struktures se databazes por e ben me te lehte punen me relationships
    # Imagjinojme sikur duam autorin e nje posti: Do marrim user_id dhe do kerkojme te User me ate id dhe aty gjejme username

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)