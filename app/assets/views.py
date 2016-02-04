from flask import render_template, flash, redirect, url_for
from flask_login import current_user

import app
from app.assets import assets
from forms import AddAssetForm


@assets.route('/')
def index():
    if current_user.has_admin:
        viewable_assets = app.models.Asset.query.all()
        heading = 'All Assets'
    else:
        viewable_assets = []  # todo: populate with assigned assets
        heading = 'Assigned Assets'
    return render_template('assets/index.html', assets=viewable_assets,
                           heading=heading)


@assets.route('/add', methods=['GET', 'POST'])
def add():
    if not current_user.has_admin:
        return render_template('errors/generic.html',
                               message="Only admins can add assets")

    form = AddAssetForm()
    if form.validate_on_submit():
        asset = app.models.Asset(
            form.name.data,
            form.type.data,
            form.description.data,
            form.serial_no.data,
            form.code.data,
            form.purchased.data,
            current_user
        )
        app.db.session.add(asset)
        app.db.session.commit()
        flash("Asset added", "success")
        return redirect(url_for('assets.index'))

    return render_template('assets/add.html', form=form, heading='Add asset')
