from flask import render_template, Blueprint, flash, url_for, redirect, request, g, jsonify
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from flask_babel import _, get_locale   
from guess_language import guess_language


blueprint = Blueprint('blueprint', __name__)


@blueprint.before_request
def before_request():
    from microblog import db
    from microblog.forms import SearchForm
    if current_user.is_authenticated:              
        current_user.last_seen = datetime.utcnow() 
        db.session.commit()                        
        g.search_form = SearchForm()
    g.locale = str(get_locale())


@blueprint.route('/', methods=['GET', 'POST'])    
@blueprint.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    from microblog.forms import BlogPostForm
    from microblog.models import Post
    from microblog import db, app
    form = BlogPostForm()
    if form.validate_on_submit():       
       
        language = guess_language(form.post.data)
        if language == "UNKNOWN" or len(language) > 5:  
            language = ''    
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been posted!")

       
       
       
        return redirect(url_for('blueprint.index'))

   
   

   
   
   
    page = request.args.get('page', 1, type=int)   

    posts = current_user.followed_posts().paginate(page, app.config['POST_PER_PAGE'], False)
   


   
    next_url = url_for('blueprint.index', page=posts.next_num) if posts.has_next else None  
    prev_url = url_for('blueprint.index', page=posts.prev_num) if posts.has_prev else None

   
    return render_template('index.html', form=form, title='Homepage',
                           posts=posts.items, next_url=next_url, prev_url=prev_url) 


@blueprint.route('/explore')
@login_required
def explore():
    from microblog.models import Post
    from microblog import app

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)

   
    next_url = url_for('blueprint.explore', page=posts.next_num) if posts.has_next else None 
    prev_url = url_for('blueprint.explore', page=posts.prev_num) if posts.has_prev else None

   
   
    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)



@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    from microblog.models import User
    from microblog.forms import LoginForm
   
   
    if current_user.is_authenticated:
        return redirect(url_for('blueprint.index'))
    form = LoginForm()
    if form.validate_on_submit():      
        user = User.query.filter_by(username=form.username.data).first() 
       
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid Username or Password"))  
            return redirect(url_for('blueprint.login'))
        login_user(user, remember=form.remember_me.data) 
       

       
        next_page = request.args.get('next')

       
       
       
        if not next_page or url_parse(next_page).netloc != '' or next_page[0] == '/':  
            next_page = url_for('blueprint.index')
        return redirect(next_page[1:])       



    return render_template('login.html', title='Sign In', form=form)


@blueprint.route('/logout')
@login_required
def logout():                    
    logout_user()
    return redirect(url_for('blueprint.login'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    from microblog import db
    from microblog.models import User
    from microblog.forms import RegistrationForm

    if current_user.is_authenticated:            
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
   
   
   
   
   

   
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).paginate(page, app.config['POST_PER_PAGE'], False)

   
    next_url = url_for('blueprint.user', username=username, page=posts.next_num) if posts.has_next else None 
    prev_url = url_for('blueprint.user', username=username, page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@blueprint.route('/edit_profile', methods=['GET', 'POST']) 
@login_required                      
def edit_profile():
    from microblog.forms import EditProfileForm
    from microblog import db

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data 
        current_user.about_me = form.about_me.data
        form.username.data = ''
        form.about_me.data = ''
        db.session.commit()
        flash("Your profile have been updated!")
        return redirect(url_for('blueprint.user', username=current_user.username))

   
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@blueprint.route('/follow/<username>') 
@login_required
def follow(username):
    from microblog.models import User
    from microblog import db
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found")  
        return redirect(url_for('blueprint.index'))
    if user == current_user:
        flash("You cannot follow yourself!")
        return redirect(url_for('blueprint.user', username=username))
    current_user.follow(user)           
    db.session.commit()                
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
                               int(os.environ.get('POSTS_PER_PAGE'))) 
    next_url = url_for('blueprint.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * int(os.environ.get('POSTS_PER_PAGE')) else None
    prev_url = url_for('blueprint.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)