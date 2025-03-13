from datetime import datetime
from app import db
from werkzeug.security import check_password_hash
from argon2 import PasswordHasher
import bleach

# Initialize Argon2 password hasher
ph = PasswordHasher()

def sanitize(input_text):
    """Sanitize user input to prevent SQL injection."""
    return bleach.clean(input_text)

class User(db.Model):
    """User model for authentication and session management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash password using Argon2id."""
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        """Verify password using Argon2id."""
        try:
            return ph.verify(self.password_hash, password)
        except:
            return False

class Room(db.Model):
    """Room model for managing chat rooms."""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash room password using Argon2id."""
        self.password_hash = ph.hash(password)
        
    def check_password(self, password):
        """Verify room password using Argon2id."""
        try:
            return ph.verify(self.password_hash, password)
        except:
            return False

class BannedIP(db.Model):
    """Model for tracking banned IP addresses per room."""
    __tablename__ = 'banned_ips'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 support
    banned_at = db.Column(db.DateTime, default=datetime.utcnow)
    banned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.String(256))
    
    __table_args__ = (
        db.UniqueConstraint('room_id', 'ip_address', name='unique_room_ip'),
    )

class FailedAttempt(db.Model):
    """Model for tracking failed login attempts."""
    __tablename__ = 'failed_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    attempt_count = db.Column(db.Integer, default=1)
    first_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    
    def increment(self):
        """Increase failed login attempt count."""
        self.attempt_count += 1
        self.last_attempt = datetime.utcnow()
