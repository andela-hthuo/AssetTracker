from flask import render_template, redirect, url_for, flash, request, \
    current_app
from flask_login import login_required
from app import csrf
from models import User, Asset


@current_app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@csrf.error_handler
def csrf_error(reason):
    return render_template(
        'error/generic.html',
        message="%s. Someone may be trying to hack this app" % reason
    ), 400


@current_app.before_request
def before_request():
    if not User.query.all():
        # if no users in the database, the app need to be set up
        if not url_for('auth.setup') in request.path and not \
                        url_for('static', filename='') in request.path:
            # unless we are already in set up or requesting a static resource
            return redirect(url_for('auth.setup'))


@current_app.route('/')
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
