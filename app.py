"""
Veritas Microfinance Bank - Main Flask Application
Entry point for the banking system
"""

from flask import Flask, render_template, session
from flask_session import Session
from config import config
from routes import auth_bp, accounts_bp, transfers_bp, admin_bp
import os


def create_app(config_name='development'):
    """
    Application factory function
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize Flask-Session
    Session(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(admin_bp)
    
    # Home route
    @app.route('/')
    def index():
        """Home page"""
        if 'customer_id' in session:
            return render_template('dashboard.html')
        return render_template('login.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        return render_template('500.html'), 500
    
    # Health check
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return {"status": "healthy", "app": "Veritas Bank"}
    
    return app


if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(host='0.0.0.0', port=5000, debug=True)
