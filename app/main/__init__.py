from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from ..models import db, User, Permission, Composition, PostType
from app.forms import EditProfileForm, AdminLevelEditProfileForm, CompositionForm
from flask_login import current_user, login_required
from ..decorators import admin_required, permission_required

main = Blueprint('main', __name__)

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission, PostType=PostType)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = CompositionForm()
    if current_user.can(Permission.PUBLISH) and form.validate_on_submit():
        composition = Composition(post_type=form.post_type.data, title=form.title.data, description=form.description.data, poster=current_user._get_current_object())
        db.session.add(composition)
        db.session.commit()
        composition.generate_slug()
        return redirect(url_for('.index'))
    page = request.args.get("page", 1, type=int)
    pagination = Composition.query.order_by(Composition.timestamp.desc()).paginate(page, per_page=current_app.config["ZOMBO_COMP_PER_PAGE"], error_out=False)
    compositions = pagination.items
    return render_template('index.html', form=form, compositions=compositions, pagination=pagination)


@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = Composition.query.filter_by(poster_id=user.id).order_by(Composition.timestamp.desc()).paginate(page, per_page=current_app.config["ZOMBO_COMP_PER_PAGE"], error_out=False)
    compositions = pagination.items
    return render_template("user.html", user=user, compositions=compositions, pagination=pagination)


@main.route("/composition/<slug>")
def composition(slug):
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    return render_template("composition.html", compositions=[composition])


@main.route("/follow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("that ain't a user here.")
        return redirect(url_for(".index"))
    if current_user.is_following(user):
        flash("u r already following dem.")
        return redirect(url_for(".user", username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"you are now following {username}.")
    return redirect(url_for(".user", username=username))

@main.route("/unfollow/<username>")
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("that ain't a user here.")
        return redirect(url_for(".index"))
    if current_user.is_a_follower(user) is None:
        flash("u r not following dem.")
        return redirect(url_for(".user", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"you are not following {username} now.")
    return redirect(url_for(".user", username=username))

@main.route("/followers/<username>")
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config["ZOMBO_FOLLOWERS_PER_PAGE"], error_out=False)
    follows = [{"user": item.follower, "timestamp": item.timestamp} for item in pagination.items]
    return render_template("followers.html", user=user, title_text="Followers of", endpoint=".followers", pagination=pagination, follows=follows)

@main.route("/following/<username>")
def following(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("invalid user.")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    pagination = user.following.paginate(page, per_page=current_app.config["ZOMBO_FOLLOWERS_PER_PAGE"], error_out=False)
    follows = [{"user": item.follower, "timestamp": item.timestamp}for item in pagination.items]


@main.route("/editprofile", methods=["GET", "POST"])
@login_required
def edit_profile():
    editprofileform = EditProfileForm()
    if editprofileform.validate_on_submit():
        current_user.name = editprofileform.name.data
        current_user.location = editprofileform.location.data
        current_user.bio = editprofileform.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You successfully updated your profile! Looks great.')
        return redirect(url_for('main.user', username=current_user.username))
    editprofileform.name.data = current_user.name
    editprofileform.location.data = current_user.location
    editprofileform.bio.data = current_user.bio
    return render_template('edit_profile.html', editprofileform=editprofileform)


@main.route("/edit_profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_profile(id):
    admineditprofile = AdminLevelEditProfileForm()
    user_profile = User.query.filter_by(id=id).first()

    if admineditprofile.validate_on_submit():
        if admineditprofile.username.data != user_profile.username:
            user_profile.username = admineditprofile.username.data
            db.session.add(user_profile.username)
        if admineditprofile.user_email.data != user_profile.user_email:
            user_profile.user_email = admineditprofile.user_email.data
            db.session.add(user_profile.user_email)
        user_profile.confirmed = admineditprofile.confirmed.data
        user_profile.role_id = admineditprofile.role.data
        user_profile.name = admineditprofile.name.data
        user_profile.location = admineditprofile.location.data
        user_profile.bio = admineditprofile.bio.data
        #db.session.add(user_profile.confirmed, user_profile.role_id, user_profile.name,user_profile.location, user_profile.bio)
        db.session.add(user_profile)
        db.session.commit()
        flash("Updated profile")

    admineditprofile.username.data = user_profile.username
    admineditprofile.user_email.data = user_profile.user_email
    admineditprofile.confirmed.data = user_profile.confirmed
    admineditprofile.role.data = user_profile.role_id
    admineditprofile.name.data = user_profile.name
    admineditprofile.location.data = user_profile.location
    admineditprofile.bio.data = user_profile.bio

    return render_template("edit_profile.html", admineditprofile=admineditprofile)