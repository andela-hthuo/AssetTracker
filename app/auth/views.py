import json
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, \
    current_app
from flask_login import login_user, logout_user, login_required, current_user
from oauth2client import client, crypt


from app import login_manager, db
from app.models import User, Role, Invitation, GoogleUser, PasswordResetRequest
from app.auth import auth, guest_required, role_required
from app.auth.forms import LoginForm, SignUpForm, InviteForm, \
    PasswordResetForm, PasswordResetRequestForm
from app.helpers import send_email, random_base64


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('error/401.html'), 401


@auth.route('/setup', methods=['GET', 'POST'])
def setup():
    # if there are users in the DB, the app is already set up
    if User.query.all():
        return redirect(url_for('index'))

    form = SignUpForm()
    if form.validate_on_submit():
        user = User(form.email.data, form.password.data, form.name.data, 'superadmin')
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Super admin created successfully", 'success')
        return redirect(url_for('index'))

    return render_template(
        'auth/setup.html',
        form=form,
        heading="Create super admin account"
    )


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # if there's a user logged in, no need to continue with log in
    if current_user.is_authenticated:
        flash("You're already logged in", "info")
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # the method is POST and the form is valid
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            url_for_next = request.args.get('next')
            # todo: validate url_for_next
            flash("Logged in successfully", 'success')
            return redirect(url_for_next or url_for('index'))
        else:
            flash("Invalid email and password combination", 'danger')

    return render_template('auth/login.html', form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", 'info')
    return redirect(url_for('index'))


@auth.route('/users/')
@login_required
def users():
    return render_template('auth/users.html', roles=Role.query.all())


@auth.route('/users/invite', methods=['GET', 'POST'])
@role_required('admin')
def invite_user():
    form = InviteForm()
    # users can only add users one privilege level below them
    form.role.choices = [(role.id, role.title) for role in Role.query.all()
                         if role.level > current_user.roles[0].level]
    if form.validate_on_submit():
        # the method is POST and the form is valid
        token = random_base64(lambda t: Invitation.get(t) is None)
        invitation = Invitation(
            token,
            form.email.data,
            Role.get_by_id(form.role.data),
            current_user
        )

        # invite_link: http://<host>/signup?invite=<token>
        invite_link = url_for('auth.signup', _external=True, invite=token)

        # prepare and send invitation email
        try:
            send_email(
                subject="Asset Tracker Invitation",
                sender=(current_user.name, current_user.email),
                recipients=[form.email.data],
                body="You've been invited to join Asset Tracker. Follow \
                    this link to sign up: %s" % invite_link,
                html="You've been invited to join Asset Tracker. Follow \
                    this link to sign up:<br> <a href=\"%s\">%s</a>" % \
                (invite_link, invite_link)
            )
            db.session.add(invitation)
            db.session.commit()
            flash("Invitation sent to %s" % form.email.data, 'success')
        except Exception, e:
            if current_app.config.get('DEBUG'):
                raise e
            else:
                flash("Failed to send invite due to a %s error"
                      % e.__class__.__name__, 'danger')
                return render_template('auth/invite.html', form=form)

        return redirect(url_for('index'))

    return render_template('auth/invite.html', form=form)


@auth.route('/users/signup', methods=['GET', 'POST'])
@guest_required
def signup():
    form = SignUpForm()
    token = request.args.get('invite')
    invite = Invitation.get(token)

    if token and not invite:
        return render_template(
            'error/generic.html',
            message="The invite is invalid"
        )

    if invite is not None:
        if User.query.filter_by(email=invite.invitee).first() is not None:
            return render_template(
                'error/generic.html',
                message="Email belongs to an existing user"
            )

    if form.validate_on_submit():
        if invite is None:
            role_short = 'staff'
        else:
            role_short = invite.role.short
            if form.email.data != invite.invitee:
                return render_template(
                    'error/generic.html',
                    message="Email doesn't match invite email"
                )

        user = User(form.email.data, form.password.data, form.name.data, role_short)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Sign up successful", 'success')
        return redirect(url_for('index'))

    if invite is not None:
        form.email.data = invite.invitee
    else:
        flash('Signing up without an inivite defaults to staff member account', 'info')
    return render_template('auth/signup.html', form=form)


@auth.route('/oauth/google', methods=['GET', 'POST'])
@guest_required
def google_sign_in():
    id_token = request.form.get('id_token')
    if not id_token:
        flash("Invalid Google sign in token", "danger")
        return redirect(url_for('auth.login', next=request.args.get('next')))

    try:
        id_info = client.verify_id_token(id_token, current_app.config['GOOGLE_CLIENT_ID'])
        if id_info['aud'] != current_app.config['GOOGLE_WEB_CLIENT_ID']:
            raise crypt.AppIdentityError("Unrecognized client.")
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
        # if id_info['hd'] != request.headers['Host']:
        #     raise crypt.AppIdentityError("Wrong hosted domain.")

    except crypt.AppIdentityError:
        flash("Invalid Google sign in token for ", "danger")
        return redirect(url_for('auth.login', next=request.args.get('next'))), 400

    google_id = id_info['sub']
    google_user = GoogleUser.query.filter_by(google_id=google_id).first()
    if not google_user:
        if User.query.filter_by(email=id_info['email']).first() is not None:
            return json.dumps({
                'flash': {
                    'category': 'danger',
                    'message': 'Email belongs to an existing user'
                }
            })

        # todo: check if user has an invite
        user = User(id_info['email'], None, id_info['name'], 'staff')
        db.session.add(user)
        db.session.commit()
        google_user = GoogleUser(google_id, user)
        db.session.add(google_user)
        db.session.commit()

    login_user(google_user.user)
    flash("Logged in successfully", "success")
    return json.dumps({
        'redirect': url_for('index')
    })


@auth.route('/password_reset', methods=['GET', 'POST'])
@guest_required
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        def accept(t):
            return PasswordResetRequest.query.filter_by(token=t).first() is None
        token = random_base64(accept)
        reset_link = url_for('auth.password_reset', _external=True, token=token)
        try:
            send_email(
                subject="Reset your Asset Tracker Password",
                sender=form.email.data,
                recipients=[form.email.data],
                body="Asset Tracker password reset link: %s\r\n\r\n\
                     This link will expire in 24 hours" % reset_link,
                html="Asset Tracker password reset link:<br> <a href=\"%s\">\
                     %s</a> <br><br>This link will expire in 24 hours" %
                     (reset_link, reset_link)
            )
            entry = PasswordResetRequest(
                token,
                User.query.filter_by(email=form.email.data).first()
            )
            db.session.add(entry)
            db.session.commit()
            flash("A link to reset your password has been sent to %s" %
                  form.email.data, "success")

        except Exception, e:
            if current_app.config.get('DEBUG'):
                raise e
            else:
                flash("Failed to send invite due to a %s error"
                      % e.__class__.__name__, 'danger')

    return render_template("auth/password_request_request.html",
                           form=form,
                           heading="Send password reset link")


@auth.route('/password_reset/<token>', methods=['GET', 'POST'])
@guest_required
def password_reset(token=None):
    reset_request = PasswordResetRequest.query.filter_by(token=token).first()
    if (reset_request is None) or reset_request.used:
        flash("Invalid password reset link", "danger")
        return redirect(url_for('.password_reset_request'))

    form = PasswordResetForm()
    if form.validate_on_submit():
        delta = datetime.now() - reset_request.time
        if delta.days > 0:
            flash("Trying to use expired password reset token", "danger")
            return redirect(url_for('.password_reset_request'))

        user = reset_request.user
        if user.email != form.email.data:
            flash("Email doesn't match password reset link", "danger")
            return render_template("auth/password_reset.html",
                                   form=form,
                                   token=token)

        user.set_password(form.password.data)
        reset_request.used = True
        db.session.add_all([user, reset_request])
        db.session.commit()
        flash("Your password has been changed", "success")
        return redirect(url_for('.login'))

    return render_template("auth/password_reset.html",
                           form=form,
                           token=token)

