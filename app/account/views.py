import os

from werkzeug import secure_filename
from flask import render_template, flash, redirect, url_for, request, \
    current_app, send_from_directory
from flask_login import current_user, login_required

from app import db
from app.models import User, Role
from app.account import account
from forms import EditProfileForm

PROFILE_PIC_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
PROFILE_PIC_UPLOAD_SUBFOLDER = 'avatars'


@account.before_request
@login_required
def before_request():
    pass


@account.route('/account')
@account.route('/users/<user_id>')
def show(user_id=None):
    if user_id is None:
        user = current_user
    elif user_id == str(current_user.id):
        return redirect(url_for('.show'))
    else:
        user = User.query.filter_by(id=user_id).first()

    return render_template(
        'account/show.html',
        user=user
    )


@account.route('/account/edit', methods=['GET', 'POST'])
def edit():
    form = EditProfileForm()
    if form.validate_on_submit():
        pic_file = request.files[form.profile_pic.name]
        if pic_file and allowed_file(pic_file.filename):
            filename = secure_filename(pic_file.filename)
            folder = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                  PROFILE_PIC_UPLOAD_SUBFOLDER)
            if not os.path.exists(folder):
                os.makedirs(folder)
            pic_file.save(os.path.join(folder, filename))
            current_user.profile_pic_url = url_for('.profile_pic',
                                                   filename=filename)

        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.add(current_user)
        db.session.commit()
        flash("Account information saved successfully", "success")
        return redirect(url_for('.show'))

    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email

    return render_template('account/edit.html', form=form)


@account.route('/users/')
def users():
    return render_template('account/users.html', roles=Role.query.all())


@account.route('/profile_pic/<filename>')
def profile_pic(filename):
    return send_from_directory(
        os.path.join(current_app.config['UPLOAD_FOLDER'],
                     PROFILE_PIC_UPLOAD_SUBFOLDER),
        filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in PROFILE_PIC_ALLOWED_EXTENSIONS
