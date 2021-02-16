from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email..."})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password..."})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    # Check if there is a user with the current typed username in the db.
    def validate_email(self, username):
        is_user = User.query.filter_by(email=self.email.data).first()
        if is_user is None:
            raise ValidationError('Try again with a correct email!')

class TestForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Sign Up')
    
    # Check if there is a user with the current typed username in the db.
    def validate_username(self, username):
        is_user = User.query.filter_by(username=username.data).first()
        if is_user:
            raise ValidationError('That username already exists! Please choose another one!')
    
    # Check if there is a user with the same type email in the db.
    def validate_email(self, email):
        is_user = User.query.filter_by(email=email.data).first()
        if is_user:
            raise ValidationError('That email already exists! Please choose another one!')

    