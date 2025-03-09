"""
Модуль моделей даних.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .content import GenerationHistory
from .payment import Payment

__all__ = ['db', 'User', 'GenerationHistory', 'Payment'] 