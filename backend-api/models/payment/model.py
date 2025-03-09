"""
Модель платежу.
"""

from datetime import datetime
from .. import db

class Payment(db.Model):
    """
    Модель платежу в базі даних.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    plan = db.Column(db.String(20), nullable=False)  # professional, premium
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = db.relationship('User', backref=db.backref('payments', lazy=True)) 