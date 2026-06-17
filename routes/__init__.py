"""
Routes package for Veritas Bank
"""

from routes.auth import auth_bp
from routes.accounts import accounts_bp
from routes.transfers import transfers_bp
from routes.admin import admin_bp

__all__ = ['auth_bp', 'accounts_bp', 'transfers_bp', 'admin_bp']
