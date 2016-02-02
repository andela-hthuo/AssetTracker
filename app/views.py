from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import app, login_manager, db
from forms import LoginForm, SignUpForm
from models import User, Role


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('errors/401.html'), 401


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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            url_for_next = request.args.get('next')
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
def index():
    return render_template('index.html')


@app.route('/users')
@login_required
def users():
    return render_template('users/index.html', users=User.query.all())
