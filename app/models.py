from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
#from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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

    def generate_confirmation_token(self, expiration_seconds=3600):
        s = Serializer(current_app.secret_key, expiration_sec)
        return s.dumps({"confirm_id": selfid}).decode("uft-8")

    def confirm(self, token):
        s = Serializer(current_app.secret_key)
        # is token valid and hasn't expired
        try:
            data = s.loads(token.encode("uft-8"))
        except:
            return False
        # does the token's data match the users
        if data.get("confirm_id") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        # the data isn't commited yet as you want to make sure the user is currently logged in.
        return True

    def __init__(self, username, user_email, password, confirmed):
        self.username = username
        self.user_email = user_email
        self.password = password
        self.confirmed = confirmed

@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))
