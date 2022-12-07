# Klasat e meposhtme nuk vijne direkt nga libraria flask_wtf por nga nje dependency e kesaj librarie qe eshte wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from microblog.models import User
from flask_babel import _, lazy_gettext as _l
from flask import request


class LoginForm(FlaskForm):
   
    username = StringField(_l('Username'), validators=[DataRequired()])   
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('repeat_password', message='Password must match')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username): 
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username already exists!")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email already exists!")


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Update')

   
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

   
    def validate_username(self, username):
       
        if username.data != self.original_username:   
            user = User.query.filter_by(username=username.data).first() 
            if user is not None:                                   
                raise ValidationError("Username already exists!")


class BlogPostForm(FlaskForm):
    post = TextAreaField('Say something!', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Post')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Password must match')])
    password2 = PasswordField('Repeat Password', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
