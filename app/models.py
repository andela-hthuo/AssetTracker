from werkzeug.security import generate_password_hash, \
     check_password_hash
from flask_login import UserMixin
from app import db

roles = db.Table(
    'roles',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
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

    def __init__(self, email, password, name):
        self.email = email
        self.password = generate_password_hash(password)
        self.name = name

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(255))

    def __init__(self, short, title, description):
        self.short = short
        self.title = title
        self.description = description

    @staticmethod
    def get(short):
        return Role.query.filter_by(short=short).first()
