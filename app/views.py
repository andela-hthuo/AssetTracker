from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import app, login_manager, db, mail, csrf
from forms import LoginForm, SignUpForm, InviteForm
from models import User, Role, Invitation, Asset
import os
import base64


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('errors/401.html'), 401


@csrf.error_handler
def csrf_error(reason):
    return render_template(
        'errors/generic.html',
        message="%s. Someone may be trying to hack this app" % reason
    ), 400


@app.before_request
def before_request():
    if not User.query.all():
        # if no users in the database, the app need to be set up
        if not url_for('setup') in request.path and not \
                        url_for('static', filename='') in request.path:
            # unless we are already in set up or requesting a static resource
            return redirect(url_for('setup'))


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    # if there are users in the DB, the app is already set up
    if User.query.all():
        return redirect(url_for('index'))

    form = SignUpForm()
    if form.validate_on_submit():
        role = Role.get('superadmin')
        user = User(form.email.data, form.password.data, form.name.data)
        role.users.append(user)
        db.session.add(user)
        db.session.add(role)
        db.session.commit()
        login_user(user)
        flash("Super admin created successfully", 'success')
        return redirect(url_for('index'))

    return render_template(
        'users/setup.html',
        form=form,
        heading="Create super admin account"
    )


@app.route('/login', methods=['GET', 'POST'])
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

    return render_template('users/login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", 'info')
    return redirect(url_for('index'))


@app.route('/')
@login_required
def index():
    all_users = User.query.all()
    all_assets = Asset.query.all()
    summary = {
        'users': len(all_users),
        'admins': len([user for user in all_users if user.is_admin]),
        'supers': len([user for user in all_users if user.is_super]),
        'staff': len([user for user in all_users if user.is_staff]),
        'assets': len(all_assets),
        'assigned': len([asset for asset in all_assets if asset.is_assigned]),
        'available': len([asset for asset in all_assets if not asset.is_assigned])
    }
    return render_template('index.html', summary=summary)


@app.route('/users/')
@login_required
def users():
    return render_template('users/index.html', roles=Role.query.all())


@app.route('/users/invite', methods=['GET', 'POST'])
@login_required
def invite_user():
    # only admins can send invites
    if not current_user.has_admin:
        return render_template('errors/generic.html',
                               message="Only admins can send invites")

    form = InviteForm()
    # users can only add users one privilege level below them
    form.role.choices = [(role.id, role.title) for role in Role.query.all()
                         if role.level > current_user.roles[0].level]
    if form.validate_on_submit():
        # the method is POST and the form is valid
        token = base64.urlsafe_b64encode(os.urandom(24))
        invitation = Invitation(
            token,
            form.email.data,
            Role.get_by_id(form.role.data),
            current_user
        )

        # invite_link: http://<host>/signup?invite=<token>
        invite_link = url_for('signup', _external=True, invite=token)

        # prepare and send invitation email
        msg = Message(
            "Inventory Manager invitation",
            # this should be sender=current_user.email but if I do that the
            # smtp email may get blacklisted as a spammer
            sender=app.config.get('MAIL_USERNAME'),
            recipients=[form.email.data])
        msg.body = "You've been invited to join Inventory Manager. Follow \
            this link to sign up: %s" % invite_link
        msg.html = "You've been invited to join Inventory Manager. Follow \
            this link to sign up:<br> <a href=\"%s\">%s</a>" % \
            (invite_link, invite_link)
        try:
            mail.send(msg)
            db.session.add(invitation)
            db.session.commit()
            flash("Invitation sent to %s" % form.email.data, 'success')
        except Exception, e:
            if app.config.get('DEBUG'):
                raise e
            else:
                flash("Failed to send invite due to a %s error"
                      % e.__class__.__name__, 'danger')
                return render_template('users/invite.html', form=form)

        return redirect(url_for('index'))

    return render_template('users/invite.html', form=form)


@app.route('/users/signup', methods=['GET', 'POST'])
def signup():
    # if there's a user logged in, no need to continue with sign up
    if current_user.is_authenticated:
        flash("You're already logged in", "info")
        return redirect(url_for('index'))

    form = SignUpForm()
    token = request.args.get('invite')
    invite = Invitation.get(token)

    if token and not invite:
        return render_template(
            'errors/generic.html',
            message="The invite is invalid"
        )

    if invite is not None:
        if User.query.filter_by(email=invite.invitee).first() is not None:
            return render_template(
                'errors/generic.html',
                message="Email belongs to an existing user"
            )

    if form.validate_on_submit():
        if invite is None:
            role = Role.get('staff')
        else:
            role = invite.role
            if form.email.data != invite.invitee:
                return render_template(
                    'errors/generic.html',
                    message="Email doesn't match invite email"
                )

        user = User(form.email.data, form.password.data, form.name.data)
        role.users.append(user)
        db.session.add_all([user, role])
        db.session.commit()
        login_user(user)
        flash("Sign up successful", 'success')
        return redirect(url_for('index'))

    if invite is not None:
        form.email.data = invite.invitee
    else:
        flash('Signing up without an inivite defaults to staff member account', 'info')
    return render_template('users/signup.html', form=form)
