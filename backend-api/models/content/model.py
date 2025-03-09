"""
Модель історії генерації контенту.
"""

from datetime import datetime
from .. import db

class GenerationHistory(db.Model):
    """
    Модель історії генерації контенту в базі даних.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    audience = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    style = db.Column(db.String(100), nullable=False)
    result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('generations', lazy=True)) 