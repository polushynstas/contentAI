"""
Модель користувача.
"""

from datetime import datetime
from .. import db

class User(db.Model):
    """
    Модель користувача в базі даних.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_subscribed = db.Column(db.Boolean, default=False)
    subscription_end = db.Column(db.DateTime, nullable=True)
    subscription_type = db.Column(db.String(20), default="free")
    request_count = db.Column(db.Integer, default=0)
    request_limit = db.Column(db.Integer, default=5)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def subscription_end_date(self):
        """
        Повертає дату закінчення підписки.
        """
        return self.subscription_end
    
    @subscription_end_date.setter
    def subscription_end_date(self, value):
        """
        Встановлює дату закінчення підписки.
        """
        self.subscription_end = value 