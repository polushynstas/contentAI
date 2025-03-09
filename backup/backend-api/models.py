from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import datetime as dt

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=dt.utcnow)
    is_subscribed = db.Column(db.Boolean, default=False)
    subscription_end = db.Column(db.DateTime, nullable=True)
    subscription_type = db.Column(db.String(20), default="none")
    request_count = db.Column(db.Integer, default=0)
    request_limit = db.Column(db.Integer, default=5)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class GenerationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    audience = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    style = db.Column(db.String(100), nullable=False)
    result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=dt.utcnow)
    
    user = db.relationship('User', backref=db.backref('generations', lazy=True))

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    plan = db.Column(db.String(20), nullable=False)  # professional, premium
    created_at = db.Column(db.DateTime, default=dt.now)
    updated_at = db.Column(db.DateTime, default=dt.now, onupdate=dt.now)
    
    def __repr__(self):
        return f'<Payment {self.payment_id}>'
