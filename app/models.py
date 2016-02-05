from datetime import datetime
from werkzeug.security import generate_password_hash, \
     check_password_hash
from flask_login import UserMixin
from app import db

roles = db.Table(
    'roles',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

assignment = db.Table(
    'assignment',
    db.Column('asset_id', db.Integer, db.ForeignKey('asset.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(66))
    name = db.Column(db.String(255))
    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('users', lazy='dynamic')
    )
    invites = db.relationship(
        'Invitation',
        backref=db.backref('sender', lazy='joined'),
        lazy='dynamic',
    )
    assets_added = db.relationship(
        'Asset',
        backref=db.backref('added_by', lazy='joined'),
        lazy='dynamic',
    )
    assets_assigned = db.relationship(
        'Asset',
        secondary=assignment,
        backref=db.backref('assigned_to', lazy='dynamic')
    )

    def __init__(self, email, password, name):
        self.email = email
        self.password = generate_password_hash(password)
        self.name = name

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_admin(self):
        return self.roles[0].short == 'admin'

    @property
    def is_super(self):
        return self.roles[0].short == 'superadmin'

    @property
    def has_admin(self):
        return self.is_admin or self.is_super

    @property
    def is_staff(self):
        return self.roles[0].short == 'staff'


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(255))
    level = db.Column(db.Integer)
    invites = db.relationship(
        'Invitation',
        backref=db.backref('role', lazy='joined'),
        lazy='dynamic',
    )

    def __init__(self, short, title, description, level):
        self.short = short
        self.title = title
        self.description = description
        self.level = level

    @staticmethod
    def get(short):
        return Role.query.filter_by(short=short).first()

    @staticmethod
    def get_by_id(role_id):
        return Role.query.filter_by(id=role_id).first()


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(20), unique=True)
    invitee = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    accepted = db.Column(db.Boolean, default=False)

    def __init__(self, token, invitee, role, sender):
        self.token = token
        self.invitee = invitee
        sender.invites.append(self)
        role.invites.append(self)

    @staticmethod
    def get(token):
        return Invitation.query.filter_by(token=token).first()


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(64))
    description = db.Column(db.Text)
    serial_no = db.Column(db.String(64))
    code = db.Column(db.String(64), unique=True)
    purchased = db.Column(db.DateTime)
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    return_date = db.Column(db.DateTime)
    lost = db.Column(db.Boolean, default=False)

    def __init__(self, name, asset_type, description, serial_no, code, purchased,
                 added_by):
        self.name = name
        self.type = asset_type
        self.description = description
        self.serial_no = serial_no
        self.code = code
        self.purchased = purchased
        self.return_date = None
        added_by.assets_added.append(self)

    def assign(self, assignee, return_date):
        self.return_date = return_date
        self.assigned_to.append(assignee)

    def reclaim(self):
        self.return_date = None
        self.assigned_to.remove(self.assignee)

    def set_lost(self, lost):
        self.lost = lost

    def check_assignee(self, user):
        return self.is_assigned and self.assignee.id == user.id

    @property
    def assignee(self):
        return self.assigned_to.first()

    @property
    def is_assigned(self):
        return self.assignee is not None

    @property
    def purchased_date(self):
        return self.purchased.strftime("%d, %b %Y")

    @property
    def return_date_(self):
        return self.return_date.strftime("%d, %b %Y")

    @property
    def return_date_past(self):
        return datetime.now() > self.return_date

    @property
    def return_date_near(self):
        delta = datetime.now() - self.return_date
        return delta.days <= 1

