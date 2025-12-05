from flask import Blueprint, request, jsonify, session
from functools import wraps
import time

auth_bp = Blueprint('auth', __name__)

ADMIN_PASSWORD = "admin123"

# Active Clients Tracking moved to backend.py

def is_localhost():
    """Check if request comes from localhost"""
    return request.remote_addr == '127.0.0.1' or request.remote_addr == '::1'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def login_or_localhost_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow if logged in OR if coming from localhost
        if session.get('logged_in') or is_localhost():
            return f(*args, **kwargs)
        return jsonify({'error': 'Unauthorized'}), 401
    return decorated_function

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if data.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
        return jsonify({'message': 'Login successful'})
    return jsonify({'error': 'Invalid password'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return jsonify({'message': 'Logged out'})

@auth_bp.route('/api/check_auth', methods=['GET'])
def check_auth():
    return jsonify({'logged_in': 'logged_in' in session})
