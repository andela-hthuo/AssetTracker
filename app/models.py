from datetime import datetime
from werkzeug.security import generate_password_hash, \
    check_password_hash
from flask_login import UserMixin, current_user
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
    profile_pic_url = db.Column(db.String(255))
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
    google_id = db.relationship(
        'GoogleUser',
        backref=db.backref('user', lazy='joined', uselist=False),
        uselist=False,
        lazy='joined',
    )

    def __init__(self, email, password, name, role_short='staff'):
        self.email = email
        self.password = generate_password_hash(password) if password else None
        self.name = name
        role = Role.get(role_short)
        role.users.append(self)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return self.password and check_password_hash(self.password, password)

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


class GoogleUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(32), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, google_id, user):
        self.google_id = google_id
        user.google_id = self


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
    token = db.Column(db.String(32), unique=True)
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
        return self.return_date and self.return_date.strftime("%d, %b %Y")

    @property
    def return_date_past(self):
        return self.return_date and datetime.now() > self.return_date

    @property
    def return_date_near(self):
        if not self.return_date:
            return None
        delta = self.return_date - datetime.now()
        return not self.return_date_past and delta.days <= 2

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'serial_no': self.serial_no,
            'code': self.code,
            'purchased_date': self.purchased_date,
            'return_date_': self.return_date_,
            'lost': self.lost,
            'is_assigned': self.is_assigned,
            'assignee': self.assignee and self.assignee.name,
            'return_date_past': self.return_date_past,
            'return_date_near': self.return_date_near,
            'is_mine': self.check_assignee(current_user),
            'added_by': self.added_by.name,
        }


class PasswordResetRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime)
    used = db.Column(db.Boolean, default=False)
    user = db.relationship('User', foreign_keys=user_id)

    def __init__(self, token, user):
        self.token = token
        self.user = user
        self.time = datetime.now()
