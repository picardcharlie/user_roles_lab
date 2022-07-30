from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError
from app.models import db, User

class SignUpForm(FlaskForm):
    username = StringField("Username", validators= [DataRequired(), Length(3, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, "username can only contain letters, numbers, dots, underscores")])
    user_email = StringField("Email", validators= [DataRequired()])
    password = PasswordField("Password", validators= [DataRequired(), Length(min=4), EqualTo('password_confirm', message="passwords do not match")])
    password_confirm = PasswordField("Confirm password", validators=[DataRequired()])
    remember_me = BooleanField("remember me")
    submit = SubmitField("Sign up")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("username already in use")

    def validate_user_email(self, field):
        if User.query.filter_by(user_email=field.data).first():
            raise ValidationError("email already in use")

class SignInForm(FlaskForm):
    username = StringField("Username", validators= [DataRequired()])
    password = PasswordField("Password", validators= [DataRequired(), Length(min=4)])
    remember_me = BooleanField("remember me")
    submit = SubmitField("Sign in")

class EditProfileForm(FlaskForm):
    name = StringField("name", validators=[Length(0, 64)])
    location = StringField("location", validators=[Length(0, 64)])
    bio = TextAreaField("bio")
    submit = SubmitField("submit changes")

class AdminLevelEditProfileForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(3,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, "username can only contain letters, numbers, dots, underscores")])
    user_email = StringField("Email", validators=[DataRequired()])
    confirmed = BooleanField("confirmed")
    role = SelectField("role", coerce=int, choices=[(6, "user"), (8, "moderator"), (16, "admin")])
    name = StringField("name", validators=[Length(0, 64)])
    location = StringField("location", validators=[Length(0, 64)])
    bio = TextAreaField("bio")
    submit = SubmitField("submit changes")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("username already in use")

    def validate_user_email(self, field):
        if User.query.filter_by(user_email=field.data).first():
            raise ValidationError("email already in use")