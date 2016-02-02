from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import app, login_manager
from forms import LoginForm
from models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@login_manager.unauthorized_handler
def unauthorized():
    return render_template('errors/401.html'), 401


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
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/users')
@login_required
def users():
    return render_template('users/index.html', users=User.query.all())
