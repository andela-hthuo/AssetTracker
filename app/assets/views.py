from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from app import db
from app.assets import assets
from app.models import Asset, User
from forms import AddAssetForm, AssignAssetForm, EditAssetForm


@assets.before_request
@login_required
def before_request():
    pass


@assets.route('/')
def index():
    if current_user.has_admin:
        query = Asset.query.order_by(Asset.id.desc())
        filter_by = request.args.get('filter_by')
        if filter_by == 'assigned':
            viewable_assets = [asset for asset in query.all()
                               if asset.is_assigned]
            heading = 'Assigned Assets'
        elif filter_by == 'unassigned':
            viewable_assets = [asset for asset in query.all()
                               if not asset.is_assigned]
            heading = 'Unassigned Assets'
        elif filter_by == 'lost':
            viewable_assets = [asset for asset in query.all()
                               if asset.lost]
            heading = 'Assets Reported Lost'
        else:
            viewable_assets = query.all()
            heading = 'All Assets'
    else:
        viewable_assets = current_user.assets_assigned
        heading = 'Assigned Assets'
    return render_template('assets/index.html', assets=viewable_assets,
                           heading=heading)


@assets.route('/add', methods=['GET', 'POST'])
def add():
    if not current_user.has_admin:
        return render_template('error/generic.html',
                               message="Only admins can add assets")

    form = AddAssetForm()
    if form.validate_on_submit():
        asset = Asset(
            form.name.data,
            form.type.data,
            form.description.data,
            form.serial_no.data,
            form.code.data,
            form.purchased.data,
            current_user
        )
        db.session.add(asset)
        db.session.commit()
        flash("Asset added", "success")
        return redirect(url_for('assets.index'))

    return render_template('assets/add.html', form=form, heading='Add asset')


@assets.route('/<asset_id>/edit', methods=['GET', 'POST'])
def edit(asset_id):
    if not current_user.has_admin:
        return render_template('error/generic.html',
                               message="Only admins can add assets")

    asset = Asset.query.filter_by(id=asset_id).first_or_404()
    form = EditAssetForm(asset_id=asset.id)

    if form.validate_on_submit():
        asset.name = form.name.data
        asset.type = form.type.data
        asset.description = form.description.data
        asset.serial_no = form.serial_no.data
        asset.code = form.code.data
        asset.purchased = form.purchased.data
        db.session.add(asset)
        db.session.commit()
        flash("Asset saved", "success")
        return redirect(url_for('assets.index'))

    if request.method == 'GET':
        form.name.data = asset.name
        form.type.data = asset.type
        form.description.data = asset.description
        form.serial_no.data = asset.serial_no
        form.code.data = asset.code
        form.purchased.data = asset.purchased

    return render_template('assets/edit.html',
                           form=form,
                           heading='Edit asset',
                           asset_id=asset.id)


@assets.route('/<asset_id>/assign', methods=['GET', 'POST'])
def assign(asset_id):
    if not current_user.has_admin:
        return render_template('error/generic.html',
                               message="Only admins can assign assets")

    asset = Asset.query.filter_by(id=asset_id).first_or_404()
    if asset.is_assigned:
        return render_template('error/generic.html',
                               message="This asset is already assigned to %s"
                                       % asset.assignee.name)

    form = AssignAssetForm()
    form.user.choices = [(user.id, "%s &lt;%s&gt;" % (user.name, user.email))
                         for user in User.query.all()
                         if user.is_staff]

    if form.validate_on_submit():
        user = User.query.filter_by(id=form.user.data).first()
        if user is not None:
            asset.assign(user, form.return_date.data)
            db.session.add_all([asset, user])
            db.session.commit()
            flash("Asset assigned to %s" % user.name, "success")
            return redirect(url_for('assets.index'))

        flash("You must select a user to assign", "danger")

    return render_template('assets/assign.html', form=form,
                           heading='Assign asset', asset=asset)


@assets.route('/<asset_id>/reclaim', methods=['POST'])
def reclaim(asset_id):
    if not current_user.has_admin:
        return render_template('error/generic.html',
                               message="Only admins can reclaim assets")

    asset = Asset.query.filter_by(id=asset_id).first_or_404()
    # copy the name 'cause assignee will be removed
    name = asset.assignee.name[:]
    asset.reclaim()
    db.session.add(asset)
    db.session.commit()

    flash("Asset reclaimed from %s" % name, "success")
    return redirect(url_for('assets.index'))


@assets.route('/<asset_id>/report/lost', methods=['POST'])
def report_lost(asset_id):
    asset = Asset.query.filter_by(id=asset_id).first_or_404()
    if not asset.check_assignee(current_user):
        return render_template(
            'error/generic.html',
            message="You can only report assets assigned to you"
        )
    asset.set_lost(True)
    db.session.add(asset)
    db.session.commit()
    flash("Reported", "success")
    return redirect(url_for('assets.index'))


@assets.route('/<asset_id>/report/found', methods=['POST'])
def report_found(asset_id):

    asset = Asset.query.filter_by(id=asset_id).first_or_404()

    if current_user.has_admin or asset.check_assignee(current_user):
        if not asset.lost:
            return render_template(
                'error/generic.html',
                message="This asset is not lost"
            )
        asset.set_lost(False)
        db.session.add(asset)
        db.session.commit()
        flash("Reported as found", "success")
        return redirect(url_for('assets.index'))

    return render_template(
        'error/generic.html',
        message="Only admins or the assigned user can mark assets found"
    )

