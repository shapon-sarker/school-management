from datetime import datetime
from app import db

class WebsiteContent(db.Model):
    """Model for storing editable website content."""
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(50), nullable=False)  # about, contact, etc.
    section = db.Column(db.String(50), nullable=False)  # header, content, footer
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<WebsiteContent {self.page}:{self.section}>' 