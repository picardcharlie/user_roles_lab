from flask import Blueprint, render_template

main = Blueprint('main', __name__)

#@main.app_context_processor
#def inject_permissions():
#    return dict(Permission=Permission)

@main.route('/')
def index():
    return render_template('index.html')
