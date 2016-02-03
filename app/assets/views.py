from flask import render_template, flash, redirect, url_for
from flask_login import current_user

import app
from app.assets import assets
from forms import AddAssetForm


@assets.route('/')
def index():
    return render_template('assets/index.html')


@assets.route('/add', methods=['GET', 'POST'])
def add():
    form = AddAssetForm()
    if form.validate_on_submit():
        pass
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
