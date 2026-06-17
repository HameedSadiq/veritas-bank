"""
Account operations routes - Deposit, Withdraw, Balance, History
"""

from flask import Blueprint, render_template, request, jsonify, session
from models.account import SavingsAccount, CurrentAccount
from models.transaction import Transaction
from routes.auth import login_required
import json

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')


@accounts_bp.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard"""
    return render_template('dashboard.html')


@accounts_bp.route('/list', methods=['GET'])
@login_required
def list_accounts():
    """Get all accounts for logged-in customer"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        customer_id = session['customer_id']
        
        query = """
            SELECT account_id, account_type, account_number, balance,
                   TO_CHAR(creation_date, 'YYYY-MM-DD') as creation_date, status
            FROM accounts
            WHERE customer_id = :1
            ORDER BY creation_date DESC
        """
        
        results = db.execute_query(query, (customer_id,))
        
        accounts = []
        for row in results:
            accounts.append({
                "account_id": row[0],
                "type": row[1],
                "number": row[2],
                "balance": float(row[3]),
                "creation_date": row[4],
                "status": row[5]
            })
        
        return jsonify({
            "status": "success",
            "accounts": accounts,
            "count": len(accounts)
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@accounts_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    """Deposit money into account"""
    if request.method == 'GET':
        return render_template('deposit.html')
    
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        amount = float(data.get('amount'))
        
        account = SavingsAccount(account_id=account_id)
        result = account.deposit(amount)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@accounts_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """Withdraw money from account"""
    if request.method == 'GET':
        return render_template('withdraw.html')
    
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        amount = float(data.get('amount'))
        
        account = SavingsAccount(account_id=account_id)
        result = account.withdraw(amount)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@accounts_bp.route('/<int:account_id>/balance', methods=['GET'])
@login_required
def get_balance(account_id):
    """Get account balance"""
    try:
        account = SavingsAccount(account_id=account_id)
        result = account.get_balance()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@accounts_bp.route('/<int:account_id>/history', methods=['GET'])
@login_required
def get_history(account_id):
    """Get transaction history for an account"""
    try:
        limit = request.args.get('limit', 20, type=int)
        transaction = Transaction()
        result = transaction.get_account_transactions(account_id, limit)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@accounts_bp.route('/create', methods=['POST'])
@login_required
def create_account():
    """Create new account"""
    try:
        data = request.get_json()
        account_type = data.get('account_type', 'SAVINGS')
        account_number = data.get('account_number')
        customer_id = session['customer_id']
        branch_id = data.get('branch_id', 1)
        
        if account_type == 'SAVINGS':
            account = SavingsAccount(
                customer_id=customer_id,
                account_number=account_number,
                branch_id=branch_id
            )
        else:
            account = CurrentAccount(
                customer_id=customer_id,
                account_number=account_number,
                branch_id=branch_id
            )
        
        result = account.create_account()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
