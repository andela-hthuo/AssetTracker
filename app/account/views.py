from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from app.models import User, Role
from app.account import account


@account.before_request
@login_required
def before_request():
    pass


@account.route('/account')
@account.route('/users/<user_id>')
def show(user_id=None):
    if user_id is None:
        user = current_user
    else:
        user = User.query.filter_by(id=user_id).first()

    return render_template(
        'account/show.html',
        user=user
    )


@account.route('/users/')
def users():
    return render_template('account/users.html', roles=Role.query.all())

