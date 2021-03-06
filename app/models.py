from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
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
    role = db.Column(db.Integer, db.ForeignKey("roles.id"))

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self, perm):
        return self.can(Permission.ADMIN)

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

    def __init__(self, username, user_email, password, confirmed, **kwargs):
        self.username = username
        self.user_email = user_email
        self.password = password
        self.confirmed = confirmed
        super().__init__(**kwargs)
        if self.role is None:
            if self.user_email == current_app.config["ZOMBO_ADMIN"]:
                self.role = Role.query.filter_by(name = "Admin").first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()

class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="roles", lazy="dynamic")

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW,
                     Permission.REVIEW,
                     Permission.PUBLISH],
            'Moderator': [Permission.FOLLOW,
                          Permission.REVIEW,
                          Permission.PUBLISH,
                          Permission.MODERATE],
            'Admin': [Permission.FOLLOW,
                      Permission.REVIEW,
                      Permission.PUBLISH,
                      Permission.MODERATE,
                      Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            # see if role is already in table
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # it's not so make a new one
                role = Role(name=r)
            role.reset_permissions()
            # add whichever permissions the role needs
            for perm in roles[r]:
                role.add_permission(perm)
            # if role is the default one, default is True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

class Permission:
    FOLLOW = 0
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16


@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))
