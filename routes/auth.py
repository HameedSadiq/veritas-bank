"""
Authentication routes - Login and Registration
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.customer import Customer
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login page"""
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.get_json()
        email = data.get('email')
        id_number = data.get('id_number')
        
        if not email or not id_number:
            return jsonify({"status": "error", "message": "Email and ID number are required"}), 400
        
        customer = Customer(email=email)
        result = customer.login(email, id_number)
        
        if result['status'] == 'success':
            session['customer_id'] = result['customer_id']
            session['customer_name'] = f"{customer.first_name} {customer.last_name}"
            session.permanent = True
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Login error: {str(e)}"}), 500


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration page"""
    if request.method == 'GET':
        return render_template('register.html')
    
    try:
        data = request.get_json()
        
        customer = Customer(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            id_number=data.get('id_number'),
            date_of_birth=data.get('date_of_birth')
        )
        
        result = customer.register()
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"Registration error: {str(e)}"}), 500


@auth_bp.route('/logout')
def logout():
    """Logout customer"""
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/check-session')
def check_session():
    """Check if user is logged in"""
    if 'customer_id' in session:
        return jsonify({
            "status": "success",
            "customer_id": session['customer_id'],
            "customer_name": session.get('customer_name')
        })
    return jsonify({"status": "error", "message": "Not logged in"}), 401
