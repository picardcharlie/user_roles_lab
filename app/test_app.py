from app import create_app
from app.models import db, User, Role, Permission

def test_app_creation():
    app = create_app("testing")
    assert app

def test_user_roles():
    app = create_app("testing")
    assert app.config
    assert "data-test.sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]
    app.app_context().push()
    db.create_all()

    #chek admin role
    Role.insert_roles()
    db.session.commit()
    admin_user = User(username="admin_test", user_email="123@456", password="catpoop", confirmed=True, role_id=16, name="doug", bio="yep")
    db.session.add(admin_user)
    db.session.commit()

    a = User.query.filter_by(username="admin_test").first()
    #print(type(a))
    assert a.is_admin()

#db.session.remove()
#db.drop_all()