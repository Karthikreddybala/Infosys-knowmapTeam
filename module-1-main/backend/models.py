from datetime import datetime, timezone
from backend.extensions import db

class User(db.Model):
    """User model for authentication and role-based access."""
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    email      = db.Column(db.String(120), unique=True, nullable=True)
    password   = db.Column(db.Text, nullable=False)
    role       = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    datasets = db.relationship("Dataset", backref="owner", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "role":       self.role,
            "created_at": self.created_at.isoformat(),
        }

class UserProfile(db.Model):
    """Stores user preferences, cross-domain interests, and saved graphs based on the AI_cybersecurity domain."""
    __tablename__ = "profiles"

    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    interests    = db.Column(db.String(255), default="AI, Cybersecurity, Networks")
    saved_graphs = db.Column(db.Text, default="[]")  # Store JSON representation of graphs
    preferences  = db.Column(db.Text, default='{"theme": "dark", "default_domain": "AI_cybersecurity"}')

    user = db.relationship("User", backref=db.backref("profile", uselist=False))

    def to_dict(self):
        import json
        return {
            "interests":    self.interests.split(",") if self.interests else [],
            "saved_graphs": json.loads(self.saved_graphs),
            "preferences":  json.loads(self.preferences)
        }

class Dataset(db.Model):
    """Dataset model for storing metadata about uploaded or fetched data."""
    __tablename__ = "datasets"

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_name = db.Column(db.String(255))
    stored_name   = db.Column(db.String(255))
    file_type     = db.Column(db.String(20))
    file_size     = db.Column(db.BigInteger)
    row_count     = db.Column(db.Integer)
    column_count  = db.Column(db.Integer)
    columns       = db.Column(db.Text)
    source        = db.Column(db.String(30), default="upload")
    upload_time   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Dataset {self.original_name}>"

    def to_dict(self):
        return {
            "id":            self.id,
            "original_name": self.original_name,
            "file_type":     self.file_type,
            "file_size":     self.file_size,
            "row_count":     self.row_count,
            "column_count":  self.column_count,
            "columns":       self.columns.split(",") if self.columns else [],
            "source":        self.source,
            "upload_time":   self.upload_time.isoformat(),
        }
