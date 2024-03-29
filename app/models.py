from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
import jwt
from datetime import datetime, timedelta
import hashlib
import bleach
import re

db = SQLAlchemy()


class Permission:
    FOLLOW = 0
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16

class PostType:
    THOUGHT = 1
    IDEA = 2
    RANT = 3


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

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
                      Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            # see if role is already in table
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # it's not so make a new one
                role = Role(name=r)
            role.reset_permission()
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


class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    following_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(64), unique = True, index = True)
    user_email = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default = False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    compositions = db.relationship("Composition", backref="poster", lazy="dynamic")
    following = db.relationship("Follow", foreign_keys=[Follow.follower_id], backref=db.backref("follower", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")
    followers = db.relationship("Follow", foreign_keys=[Follow.following_id], backref=db.backref("following", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")

#     following = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'),
#                                 lazy='dynamic',
#                                 cascade='all, delete-orphan')
#     followers = db.relationship('Follow',
#                                 foreign_keys=[Follow.following_id],
#                                 backref=db.backref('following', lazy='joined'),
#                                 lazy='dynamic',
#                                 cascade='all, delete-orphan')
    def can(self, perm):
        return self.role_id is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def admin_test():
        a = User(username="admin_test", user_email="123@456", password="catpoop", confirmed=True, role_id=None, name="doug", bio="yep", avatar_hash=None)
        db.session.add(a)
        db.session.commit()

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

    def unicornify(self, size=96):
        url = "https://unicornify.pictures/avatar"
        hash = self.avatar_hash or self.email_hash()
        return f"{url}/{hash}?s={size}"

    def email_hash(self):
        return hashlib.md5(self.user_email.lower().encode("utf-8")).hexdigest()

    #follower helper functions
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, following=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.following.filter_by(following_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(following_id=user.id).first() is not None

    def is_a_follower(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def __init__(self, username, user_email, password, confirmed, avatar_hash, **kwargs):
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
        if self.user_email is not None and self.avatar_hash is None:
            self.avatar_hash = self.email_hash()


class Composition(db.Model):
    __tablename__ = "compositions"
    id = db.Column(db.Integer, primary_key=True)
    post_type = db.Column(db.Integer)
    title = db.Column(db.String(64))
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    slug = db.Column(db.String(128), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def on_changed_description(target, value, oldvalue, initiator):
        allowed_tags = ["a"]
        html = bleach.linkify(bleach.clean(value, tags=allowed_tags, strip=True))
        target.desciption_html = html

    def generate_slug(self):
        self.slug = f"{self.id}-" + re.sub(r'[^\w]+', '-', self.title.lower())
        db.session.add(self)
        db.session.commit()

db.event.listen(Composition.description, "set", Composition.on_changed_description)


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))
