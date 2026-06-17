"""
Transfer routes - Money transfer between accounts
"""

from flask import Blueprint, render_template, request, jsonify, session
from models.transfer import TransferService
from routes.auth import login_required

transfers_bp = Blueprint('transfers', __name__, url_prefix='/transfers')


@transfers_bp.route('/page', methods=['GET'])
@login_required
def transfer_page():
    """Transfer page"""
    return render_template('transfer.html')


@transfers_bp.route('/send', methods=['POST'])
@login_required
def send_transfer():
    """Send money transfer"""
    try:
        data = request.get_json()
        from_account_id = data.get('from_account_id')
        to_account_id = data.get('to_account_id')
        amount = float(data.get('amount'))
        description = data.get('description', 'Transfer')
        
        service = TransferService()
        result = service.transfer_funds(from_account_id, to_account_id, amount, description)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@transfers_bp.route('/<int:account_id>/history', methods=['GET'])
@login_required
def get_history(account_id):
    """Get transfer history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        service = TransferService()
        result = service.get_transfer_history(account_id, limit)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
