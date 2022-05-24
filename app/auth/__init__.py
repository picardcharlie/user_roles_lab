from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.forms import SignUpForm, SignInForm
from app.models import User, db
from flask_login import current_user, login_required, login_user, logout_user

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/register", methods=["GET", "POST"])
def register():
    signupform = SignUpForm()
    if signupform.validate_on_submit():
        register_user = User(signupform.username.data, signupform.password.data)
        db.session.add(register_user)
        db.session.commit()
        return redirect(url_for("main.index"))
    return render_template("/auth/register.html", signupform = signupform)

@auth.route("/login", methods=["GET", "POST"])
def login():
    signinform = SignInForm()
    if signinform.validate_on_submit():
        login_username = signinform.username.data
        login_password = signinform.password.data
        check_login_user = User.query.filter_by(username=login_username).first()
        if check_login_user is not None:
            if check_login_user.username == login_username and check_login_user.verify_password(login_password) == True:
                login_user(check_login_user, remember=signinform.remember_me.data)
                next = request.args.get("next")
                if next is None or not next.startswith("/"):
                    next = url_for("main.index")
                return redirect(next)
            else:
               flash("username and password don't match.")
        else:
            flash("username not found.")
    return render_template("/auth/login.html", signinform=signinform)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@auth.route("/secret")
@login_required
def secret():
    return render_template("/auth/secret.html")