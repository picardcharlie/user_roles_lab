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

    #check admin role
    Role.insert_roles()
    db.session.commit()
    admin_user = User(username="admin_test", user_email="123@456", password="catpoop", confirmed=True, role_id=0, name="doug", bio="yep")
    admin_user.role.add_permission(Permission.ADMIN)
    db.session.add(admin_user)
    db.session.commit()

    a = User.query.filter_by(username="admin_test").first()
    #print(type(a))
    assert a.is_admin()
    #assert a.role_id == Permission.ADMIN #this works for checking the role ID...

def test_remove_db():
    db.session.remove()
    db.drop_all()

# Optional Task: Write unit tests that test the following:
#
#     That your permission helper functions work
#     That your roles' names are successfully assigned after Role.insert_roles() is called
#     That the User, Mod, and Admin roles each have the correct permissions
#     That a new user has the User role automatically assigned by default

