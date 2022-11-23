from sqlalchemy.exc import IntegrityError
from faker import Faker
#from . import db
from .models import db, User, Composition
from random import randint
import string


def users(count=20):
    fake = Faker()
    i = 0
    while i < count:
        u = User(user_email=fake.email(),
                 username=fake.user_name(),
                 password="password",
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 bio=fake.text(),
                 last_seen=fake.past_date(),
                 avatar_hash=None)
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def compositions(count=50):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, (user_count - 1))).first()
        c = Composition(post_type=randint(1, 3),
                        title=string.capwords((fake.bs())),
                        description=fake.text(),
                        timestamp=fake.past_date(),
                        poster_id=u.id)
        db.session.add(c)
    db.session.commit()