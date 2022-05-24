from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError
from app.models import db, User

class SignUpForm(FlaskForm):
    username = StringField("Username", validators= [DataRequired(), Length(3, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, "username can only contain letters, numbers, dots, underscores")])
    password = PasswordField("Password", validators= [DataRequired(), Length(min=4), EqualTo('password_confirm', message="passwords do not match")])
    password_confirm = PasswordField("Confirm password", validators=[DataRequired()])
    remember_me = BooleanField("remember me")
    submit = SubmitField("Sign up")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("username already in use")

class SignInForm(FlaskForm):
    username = StringField("Username", validators= [DataRequired()])
    password = PasswordField("Password", validators= [DataRequired(), Length(min=4)])
    remember_me = BooleanField("remember me")
    submit = SubmitField("Sign in")