"""
User Authentication Module
Handles user registration, login, and session management.
"""

import secrets
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    has_keys      = db.Column(db.Boolean, default=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class ShareToken(db.Model):
    """
    Stores share tokens for encrypted files.
    Anyone with the token + decryption password can download and decrypt the file.
    """
    __tablename__ = 'share_tokens'

    id              = db.Column(db.Integer, primary_key=True)
    token           = db.Column(db.String(32), unique=True, nullable=False, index=True)
    owner_username  = db.Column(db.String(80), nullable=False)
    filename        = db.Column(db.String(256), nullable=False)
    original_name   = db.Column(db.String(256), nullable=False)
    password_hash   = db.Column(db.String(256), nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at      = db.Column(db.DateTime, nullable=True)
    download_count  = db.Column(db.Integer, default=0)
    max_downloads   = db.Column(db.Integer, default=10)
    is_active       = db.Column(db.Boolean, default=True)

    @staticmethod
    def generate_token():
        """Generate a secure random 8-character uppercase share code."""
        return secrets.token_hex(4).upper()

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_expired(self):
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False

    @property
    def is_valid(self):
        return (
            self.is_active and
            not self.is_expired and
            self.download_count < self.max_downloads
        )

    def __repr__(self):
        return f'<ShareToken {self.token} → {self.filename}>'
