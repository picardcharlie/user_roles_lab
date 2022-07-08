from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
import jwt
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(64), unique = True, index = True)
    user_email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default = False)

    @property
    def password(self):
        raise AttributeError("don't look at this!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        expiration_datetime = datetime.utcnow() + timedelta(seconds=3600)
        data = {"exp": expiration_datetime, "confirm_id": self.id}
        token = jwt.encode(data, current_app.secret_key, algorithm="HS512")
        return token

    def confirm(self, token):
        # is token valid and hasn't expired
        try:
            data = jwt.decode(token, current_app.secret_key, algorithms=["HS512"]) #s.loads(token.encode("uft-8"))
        except:
            return False
        # does the token's data match the users
        if data.get("confirm_id") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)

        # the data isn't commited yet as you want to make sure the user is currently logged in.
        return True

        # ...
        data = jwt.decode(token, current_app.secret_key, algorithms=["HS512"])

    def __init__(self, username, user_email, password, confirmed):
        self.username = username
        self.user_email = user_email
        self.password = password
        self.confirmed = confirmed

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")


@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))
