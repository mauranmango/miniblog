from flask import render_template, Blueprint, flash, url_for, redirect, request, g, jsonify
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from flask_babel import _, get_locale    #
from guess_language import guess_language


blueprint = Blueprint('blueprint', __name__)


# Sa here perdoruesi ben request nje faqe do updatojme last seen ne databaze.
# Por perpara se te behet nje kerkese ekzukutohet kjo metode before_request
@blueprint.before_request
def before_request():
    from microblog import db
    from microblog.forms import SearchForm
    if current_user.is_authenticated:               # Do shohim nqs useri eshte i loguar
        current_user.last_seen = datetime.utcnow()  # Atehere do updateojme atributin last_seen
        db.session.commit()                         # Updatojme databazen
        g.search_form = SearchForm()
# Nuk e shtuam objektin ne session se nqs useri eshte i loguar atehere flask e shton ne session kur thirret user_loader
    g.locale = str(get_locale())


@blueprint.route('/', methods=['GET', 'POST'])     # Meqe shtuam forme do shtojme dhe metodat Get, Post
@blueprint.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    from microblog.forms import BlogPostForm
    from microblog.models import Post
    from microblog import db, app
    form = BlogPostForm()
    if form.validate_on_submit():        # STANDARD FORM VALIDATE
        # Ketu ku procesojme postimet do therrasim funksionin qe merr si atribut postimin qe kemi futur
        language = guess_language(form.post.data)
        if language == "UNKNOWN" or len(language) > 5:   # Nqs nuk funksionon do ktheje UNKNOWN
            language = ''     # Per kete postim kur gjuha eshte Unknown apo gjatesia me e madhe se 5 do e lejme bosh
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been posted!")

        # Eshte praktike e mire te bejme redirect te faqja qe jemi pa renderuar templaten direkt.
        # Konsiderohet si praktike e keqe te renderojme nje faqe html si nje pergjigje te nje kerkese Post, sepse
        # ndodh qe kur i japim refresh faqes mund te ridergoje dhe njehere kerkesen post dhe ben submit te dhenat
        return redirect(url_for('blueprint.index'))

    # user['username'] eshte njelloj me user.username
    # user = {'username': 'Mauran'} (fake user)

    # Do na shfaqi postimet e userave qe ndjekim dhe postimet tona duke perdorur paginate ne vend te all.
    # Metoda paginate merr 3 argumente (1 faqja qe do renderohet, 2 Post per page, 3 nqs faqja nuk gjendet (empty list)
    # Duam qe argumenti i pare "page" te merret nga request dhe per kete krijojme nje variabel page
    page = request.args.get('page', 1, type=int)    # query string argument ku default eshte 1

    posts = current_user.followed_posts().paginate(page, app.config['POST_PER_PAGE'], False)
    # Paginate kthen nje objekt paginate dhe lista e rezultateve eshte brenda ketij objekti si atribut items


    # Do shtojme linqet e pagination poshte postimeve. Next & Previous
    next_url = url_for('blueprint.index', page=posts.next_num) if posts.has_next else None   # nqs do kete faqe thirret
    prev_url = url_for('blueprint.index', page=posts.prev_num) if posts.has_prev else None

    # template placeholders duhet te kalohen si argument
    return render_template('index.html', form=form, title='Homepage',
                           posts=posts.items, next_url=next_url, prev_url=prev_url)  # one page at a time


@blueprint.route('/explore')
@login_required
def explore():
    from microblog.models import Post
    from microblog import app

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)

    # Do shtojme linqet e pagination poshte postimeve. Next & Previous
    next_url = url_for('blueprint.explore', page=posts.next_num) if posts.has_next else None  # nqs do kete faqe thirret
    prev_url = url_for('blueprint.explore', page=posts.prev_num) if posts.has_prev else None

    # Do perdorim te njejten template por me titull tjeter. I vetmi problem eshte forma qe duhet ta shmangim.
    # Do shtojme pak logjike te template html. Nqs forma eshte percaktuar atehere do e shfaqim ne te kundert jo
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)



@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    from microblog.models import User
    from microblog.forms import LoginForm
    # is_authenticated eshte 1/4 property qe vjen me klasen UserMixin dhe shtohet ne modelin User
    # Pra nqs perdoruesi eshte i autentikuar atehere nuk ka pse te aksesojme formen login
    if current_user.is_authenticated:
        return redirect(url_for('blueprint.index'))
    form = LoginForm()
    if form.validate_on_submit():       # Kjo forme evaluohet True nqs fushat plotesohet ose jane te vlefshme
        user = User.query.filter_by(username=form.username.data).first()  # do shohim nqs ekziston username qe futem
        # kjo praktike eshte e mire sepse mund te ndodhi qe te na thyejne pass nqs jemi me teper specifik
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid Username or Password"))   #  Pasi importuam funksionin _ (underscore) "mbeshtollem" nje mesazh qe duam te perkthejme
            return redirect(url_for('blueprint.login'))
        login_user(user, remember=form.remember_me.data)  # argumenti remember ruan ne session userin e loguar
        # flash(f"Login Successfully for user: {form.username.data}, remember_me: {form.remember_me.data}")

        # Për ta bërë përvojën e përdoruesit me te mire do e ridrejtojme përdoruesin në faqen që synonte të vizitonte
        next_page = request.args.get('next')

        # E bejme funksionin me robust duke shmangur sulm duke vendosur ne url nje next (keqdashes) ndryshe nga "path"
        # if .netloc != '', kontrollon nese rezultati i url nga url_parse(next_page) eshte URL relative
        # A relative URL relative permban vetem  'path' dhe jo 'hostname' (URL relative --> docs.python.org:80)
        if not next_page or url_parse(next_page).netloc != '' or next_page[0] == '/':   #  Nqs nuk kemi next page do e ridrejtojme te index
            next_page = url_for('blueprint.index')
        return redirect(next_page[1:])        # Na duhet qe pasi te validohet forma te shkoje te homepage



    return render_template('login.html', title='Sign In', form=form)


@blueprint.route('/logout')
@login_required
def logout():                     #  Ky funksion do fshije session e userit
    logout_user()
    return redirect(url_for('blueprint.login'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    from microblog import db
    from microblog.models import User
    from microblog.forms import RegistrationForm

    if current_user.is_authenticated:             # Ndalojme userat qe jane loguar qe te rregjistrohen
        return redirect(url_for('blueprint.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have been registered!')
        return redirect(url_for('blueprint.login'))

    return render_template('register.html', title="Register", form=form)


@blueprint.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    from microblog.forms import ResetPasswordRequestForm
    from microblog.models import User
    from microblog.e_mail import send_password_reset_email
    if current_user.is_authenticated:
        return redirect(url_for("blueprint.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash("Check email!")
            return redirect(url_for("blueprint.login"))
    return render_template("reset_password_request.html", title='Reset Password', form=form)


@blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from microblog.models import User
    from microblog.forms import ResetPasswordForm
    from microblog import db
    if current_user.is_authenticated:
        return redirect(url_for("blueprint.index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("blueprint.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset")
        return redirect(url_for('blueprint.login'))
    return render_template('reset_password.html', form=form)




@blueprint.route('/user/<username>')
@login_required
def user(username):
    from microblog.models import User, Post
    from microblog import app
    user = User.query.filter_by(username=username).first_or_404()
    # Create a couple of fake posts
    # posts = [
    #     { 'author': user,
    #      'body': "This is the text for post1" }
    # ]

    # Filtrojme postimet sipas perdoruesve
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)

    # Do shtojme linqet e pagination poshte postimeve. Next & Previous
    next_url = url_for('blueprint.user', username=username, page=posts.next_num) if posts.has_next else None  # nqs do kete faqe thirret
    prev_url = url_for('blueprint.user', username=username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


#Flask reloader quhet ky feature dhe eshte pjese e debug mode. Pra nuk na duhet te startojme apo stopojme aplikacionin sa here bejme ndryshim.
@blueprint.route('/edit_profile', methods=['GET', 'POST'])  # Route(view) do procesoje nje web form  prandaj na duhen metodat GET, POST
@login_required                       # Do e bejme kete route te mbrojtur nga perdoruesit e paautorizuar
def edit_profile():
    from microblog.forms import EditProfileForm
    from microblog import db

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data  # My user is stored in current_user
        current_user.about_me = form.about_me.data
        form.username.data = ''
        form.about_me.data = ''
        db.session.commit()
        flash("Your profile have been updated!")
        return redirect(url_for('blueprint.user', username=current_user.username))

    # Kjo eshte menyra e dyte se si te para-popullojme format. E para behet ne template duke shtuar argumentin value
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@blueprint.route('/follow/<username>')  # URL dinamike. Kjo do jete URL e e userit te cilinn useri i loguar do te ndjeke
@login_required
def follow(username):
    from microblog.models import User
    from microblog import db
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found")   # Flask-Babel perdor stilin e vjeter per replacement string  " User %(username) not found ", username=username dhe username shtohet si kw argument
        return redirect(url_for('blueprint.index'))
    if user == current_user:
        flash("You cannot follow yourself!")
        return redirect(url_for('blueprint.user', username=username))
    current_user.follow(user)            # Ndjekim userin
    db.session.commit()                 # Ruajme ndryshimet ne databaze
    flash(f"You are now following {username}")
    return redirect(url_for('blueprint.user', username=username))


@blueprint.route('/unfollow/<username>')
@login_required
def unfollow(username):
    from microblog.models import User
    from microblog import db
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found")
        return redirect(url_for('blueprint.index'))
    if user == current_user:
        flash("You cannot unfollow yourself!")
        return redirect(url_for('blueprint.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You unfollowed {username}")
    return redirect(url_for('blueprint.user', username=username))


@blueprint.route('/translate', methods=['POST'])
@login_required
def translate_text():
    from microblog.translate import translate
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@blueprint.route('/search')
@login_required
def search():
    from microblog.models import Post
    from flask import current_app
    import os
    if not g.search_form.validate():
        return redirect(url_for('blueprint.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               int(os.environ.get('POSTS_PER_PAGE')))  #  config['POSTS_PER_PAGE'])
    next_url = url_for('blueprint.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * int(os.environ.get('POSTS_PER_PAGE')) else None
    prev_url = url_for('blueprint.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)