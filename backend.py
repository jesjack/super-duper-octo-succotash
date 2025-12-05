from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import database
import time
from functools import wraps

# Blueprints
from routes.auth import auth_bp, login_or_localhost_required, is_localhost
from routes.products import products_bp
from routes.sales import sales_bp

app = Flask(__name__)
app.secret_key = "super_secret_key" # Required for session
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(sales_bp)

# --- Frontend Routes (MPA) ---

def login_required_page(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if session.get('logged_in') or is_localhost():
        return redirect(url_for('dashboard_page'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == "admin123":
            session['logged_in'] = True
            return redirect(url_for('dashboard_page'))
        else:
            return render_template('login.html', error="Contraseña incorrecta", logged_in=False)
    
    if session.get('logged_in'):
        return redirect(url_for('dashboard_page'))
    return render_template('login.html', logged_in=False)

@app.route('/logout')
def logout_page():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/dashboard')
@login_or_localhost_required
def dashboard_page():
    return render_template('dashboard.html', active_page='dashboard', logged_in=session.get('logged_in'))

@app.route('/products')
@login_required_page
def products_page():
    return render_template('products.html', active_page='products', logged_in=True)

@app.route('/products/new')
@login_required_page
def new_product_page():
    return render_template('product_form.html')

@app.route('/products/edit/<int:id>')
@login_required_page
def edit_product_page(id):
    return render_template('product_form.html', product_id=id)

@app.route('/session/edit_cash')
@login_required_page
def edit_cash_page():
    session_info = database.get_active_session()
    current_cash = session_info['initial_cash'] if session_info else 0
    return render_template('edit_cash.html', current_cash=current_cash)

# --- Status Logic ---
connected_clients = {} # {ip: {'last_seen': time, 'logged_in': bool}}

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    is_logged_in = data.get('logged_in', False)
    client_ip = request.remote_addr
    
    # Debug heartbeat source
    # print(f"HEARTBEAT: IP={client_ip}, LoggedIn={is_logged_in}")
    
    connected_clients[client_ip] = {
        'last_seen': time.time(),
        'logged_in': is_logged_in
    }
    return jsonify({'success': True})

@app.route('/api/server_status')
def server_status():
    # Clean up old clients (> 10s)
    now = time.time()
    to_remove = [ip for ip, data in connected_clients.items() if now - data['last_seen'] > 10]
    for ip in to_remove:
        del connected_clients[ip]
        
    # Filter out localhost (POS App)
    external_clients = {ip: data for ip, data in connected_clients.items() if ip != '127.0.0.1'}
    
    count = len(external_clients)
    logged_in_count = sum(1 for data in external_clients.values() if data['logged_in'])
    
    # Logic Refined:
    # Gray: 0 connections
    # Yellow: Connections exist, but 0 logged in (Lurkers)
    # Green: Exactly 1 connection, and it is logged in (Clean Admin)
    # Orange: 1 logged in, but extra connections exist (Suspicious)
    # Purple: > 1 logged in (Multiple Admins - Danger)
    
    if count == 0:
        status_color = 'gray'
    elif logged_in_count == 0:
        status_color = '#FFC107' # Amber/Yellow (Lurkers)
    elif logged_in_count == 1:
        if count == 1:
            status_color = '#28a745' # Green (Clean)
        else:
            status_color = '#F59E0B' # Orange (Suspicious - Admin + Lurkers)
    else:
        status_color = '#6f42c1' # Purple (Multiple Admins)
        
    return jsonify({
        'status': 'online',
        'active_clients': count,
        'logged_in_clients': logged_in_count,
        'color': status_color,
        'clients_detail': external_clients # Debug info
    })

if __name__ == '__main__':
    database.init_db()
    # Run without reloader to ensure process termination works correctly from POS app
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
