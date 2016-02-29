from functools import wraps

from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user, login_required

from app.models import Role
auth = Blueprint('auth', __name__)


def guest_required(func):
    """
    If you decorate a view with this, it will ensure that there isn't an
    authenticated user before calling the actual view. (If there is , it
    redirects to the front page and flashes a message that the user is already
    logged in) For example::

     @app.route('/login')
     @guest_required
     def login():
         pass

    :param func: The view function to decorate.
    :type func: function
    """
    def _check_guest(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You're already logged in", "info")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return wraps(func)(_check_guest)


def role_required(role):
    """
    If you decorate a view with this, it will ensure that the current user is
    logged in and has the specified role before calling the actual view. (If
    they are not, it shows an error message: 'Only <role> are allowed to
    access this page') For example::

     @app.route('/admin')
     @role_required('admin')
     def admin():
         pass

    :param func: The view function to decorate.
    :type func: function
    """
    def _role_required(func):
        @login_required
        def _check_role(*args, **kwargs):
            required_role = Role.get(role)
            if current_user.roles[0].level > required_role.level:
                return render_template('error/generic.html',
                               message="Only %ss are allowed to access this \
                               page" % required_role.title)
            return func(*args, **kwargs)
        return wraps(func)(_check_role)
    return _role_required

from app.auth import views
