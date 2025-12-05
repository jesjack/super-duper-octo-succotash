from flask import Blueprint, jsonify, request
import database
import database
from flask import session
from routes.auth import login_required, login_or_localhost_required, is_localhost

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/api/sales', methods=['GET'])
@login_or_localhost_required
def get_sales():
    # If Admin: Show all sales
    if session.get('logged_in'):
        sales = database.get_all_sales()
        return jsonify({'sales': sales, 'is_admin': True})
    
    # If Localhost (Public): Show only current session sales
    session_info = database.get_active_session()
    if session_info:
        sales = database.get_sales_by_session(session_info['id'])
        return jsonify({'sales': sales, 'is_admin': False})
    
    return jsonify({'sales': [], 'is_admin': False})

@sales_bp.route('/api/stats', methods=['GET'])
@login_or_localhost_required
def get_stats():
    stats = {}
    
    # 1. Current Session Data (Always visible for localhost/admin)
    session_info = database.get_active_session()
    if session_info:
        current_sales = database.get_sales_by_session(session_info['id'])
        session_total = sum(s['total'] for s in current_sales)
        initial_cash = session_info['initial_cash']
        
        stats['current_session'] = {
            'initial_cash': initial_cash,
            'sales_total': session_total,
            'box_total': initial_cash + session_total,
            'sale_count': len(current_sales)
        }
    else:
        stats['current_session'] = None

    # 2. Historical Data (Only for Admin)
    if session.get('logged_in'):
        all_sales = database.get_all_sales()
        total_revenue = sum(s['total'] for s in all_sales)
        stats['historical'] = {
            'total_revenue': total_revenue,
            'total_count': len(all_sales)
        }
    
    return jsonify(stats)

@sales_bp.route('/api/session/update_cash', methods=['POST'])
@login_required
def update_cash():
    data = request.json
    new_amount = data.get('amount')
    
    if new_amount is None:
        return jsonify({'error': 'Amount required'}), 400
        
    session_info = database.get_active_session()
    if not session_info:
        return jsonify({'error': 'No active session'}), 404
        
    database.update_session_initial_cash(session_info['id'], float(new_amount))
    return jsonify({'success': True})
