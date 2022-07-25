import os
from app import create_app
from flask_migrate import Migrate
from app.models import db, User, Permission, Role
#db, user, post, etc

app = create_app(os.getenv("FLASK_CONFIG") or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db = db, User = User, Permission = Permission, Role = Role) #db, user, post, etc