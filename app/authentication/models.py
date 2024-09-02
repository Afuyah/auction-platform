
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app.auction.models import Auction
from datetime import datetime, timedelta
import uuid



# Association Table for Many-to-Many relationship between User and Role
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<UserRoles User ID: {self.user_id}, Role ID: {self.role_id}>'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean, default=False)  # For account activation status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    # Example: Additional relationships (e.g., bids, auctions) can be added here
    auctions = db.relationship('Auction', back_populates='user')


    # Account Activation Token
    activation_token = db.Column(db.String(64), unique=True, nullable=True)
    # Password Reset Token
    reset_token = db.Column(db.String(64), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.activation_token:
            self.activation_token = self.generate_token()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        return uuid.uuid4().hex

    def activate_account(self):
        self.active = True
        self.activation_token = None  # Invalidate the token after activation

    def generate_reset_token(self):
        self.reset_token = self.generate_token()
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour

    def verify_reset_token(self, token):
        if self.reset_token == token and self.reset_token_expiry > datetime.utcnow():
            return True
        return False

    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role):
        if role in self.roles:
            self.roles.remove(role)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def __repr__(self):
        return f'<User {self.username}>'

    # Additional methods can be added here for account management, e.g., password reset

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Role {self.name}>'

    def add_permission(self, permission):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission):
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission_name):
        return any(permission.name == permission_name for permission in self.permissions)

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = db.relationship('Role', secondary='role_permissions', backref=db.backref('permissions', lazy='dynamic'))

    def __repr__(self):
        return f'<Permission {self.name}>'

class RolePermissions(db.Model):
    __tablename__ = 'role_permissions'
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RolePermissions Role ID: {self.role_id}, Permission ID: {self.permission_id}>'
