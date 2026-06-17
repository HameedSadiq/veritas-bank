"""
Configuration settings for Veritas Bank Flask application
"""

import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'veritas-bank-secret-key-2024'
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False
    
    # Database Configuration
    DB_HOST = 'localhost'
    DB_PORT = 1521
    DB_SERVICE = 'xe'
    DB_USER = 'system'
    DB_PASSWORD = 'oracle'
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Application Configuration
    ITEMS_PER_PAGE = 10
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
