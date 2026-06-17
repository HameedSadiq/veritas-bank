"""
Admin dashboard routes
"""

from flask import Blueprint, render_template, request, jsonify, session
from models.transfer import AuditLogger
from routes.auth import login_required
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, any logged-in user can access admin (implement proper roles later)
        if 'customer_id' not in session:
            return jsonify({"status": "error", "message": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    return render_template('admin_dashboard.html')


@admin_bp.route('/audit-logs', methods=['GET'])
@admin_required
def get_audit_logs():
    """Get audit logs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        account_id = request.args.get('account_id', type=int)
        customer_id = request.args.get('customer_id', type=int)
        
        logger = AuditLogger()
        result = logger.get_audit_logs(account_id, customer_id, limit)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics():
    """Get banking statistics"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        # Total customers
        result = db.execute_query("SELECT COUNT(*) FROM customers")
        total_customers = result[0][0] if result else 0
        
        # Total accounts
        result = db.execute_query("SELECT COUNT(*) FROM accounts")
        total_accounts = result[0][0] if result else 0
        
        # Total balance
        result = db.execute_query("SELECT SUM(balance) FROM accounts")
        total_balance = float(result[0][0]) if result and result[0][0] else 0
        
        # Recent transactions
        result = db.execute_query("SELECT COUNT(*) FROM transactions WHERE transaction_date > TRUNC(SYSDATE)")
        today_transactions = result[0][0] if result else 0
        
        return jsonify({
            "status": "success",
            "total_customers": total_customers,
            "total_accounts": total_accounts,
            "total_balance": total_balance,
            "today_transactions": today_transactions
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
