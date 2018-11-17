from webapp.ext import db
from flask_security import SQLAlchemyUserDatastore, UserMixin, RoleMixin

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime(timezone=''))
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(32))
    current_login_ip = db.Column(db.String(132))
    login_count = db.Column(db.Integer())
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)

