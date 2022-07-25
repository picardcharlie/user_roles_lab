from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.forms import SignUpForm, SignInForm
from app.models import User, db, load_user
from flask_login import current_user, login_required, login_user, logout_user
from app.email import send_mail
from ..decorators import admin_required, permission_required
from ..models import Permission


auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/register", methods=["GET", "POST"])
def register():
    signupform = SignUpForm()
    if signupform.validate_on_submit():
        register_user = User(username=signupform.username.data, user_email=signupform.user_email.data, password=signupform.password.data, confirmed=False, name="", location="", bio="")
        db.session.add(register_user)
        db.session.commit()
        generate_token = register_user.generate_confirmation_token()
        send_mail(register_user.user_email, "welcome", "mail/welcome", user=register_user)
        send_mail(register_user.user_email, "confirm", "auth/mail/confirm", user=register_user, token=generate_token)
        send_mail("su4440500@gmail.com", "new user joined", "mail/new_user", user=register_user)
        return redirect(url_for("main.index"))
    return render_template("/auth/register.html", signupform = signupform)

@auth.route("/resend_confirm")
def resend_confirm():
    new_token = current_user.generate_confirmation_token()
    send_mail(current_user.user_email, "confirm", "auth/mail/confirm", user=current_user, token=new_token)
    return redirect(url_for("main.index"))

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

#accepts a link with a token and attempts to confirm the user.  Redirects after.
@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        flash("User pre-confirmed")
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        db.session.commit()
        flash("Thank you for confirming your account")
    else:
        flash("Confirmation link expired or invalid.")
    return redirect(url_for("main.index"))

@auth.before_app_request
def before_request():
    #checks if current user is logged in
    # if they have done their confirmation email
    # blocks everything except for auth routes so they can still confirm their account
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request != "static" \
                and request.blueprint != "auth" \
                and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))

@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html", user=current_user)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@auth.route("/secret")
@login_required
def secret():
    return render_template("/auth/secret.html")

@auth.route("/admin")
@login_required
@admin_required
def admin_only():
    return "Hello admin(istrator)"

@auth.route("/moderator")
@login_required
@permission_required(Permission.MODERATE)
def moderator_only():
    return "take control moderator"