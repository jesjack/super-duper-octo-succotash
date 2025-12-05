import sqlite3
import datetime

DB_NAME = "pos_system.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image_path TEXT
        )
    ''')
    
    # Migration for existing table
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN image_path TEXT")
    except sqlite3.OperationalError:
        pass # Column likely exists
    
    # Sessions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            initial_cash REAL,
            final_cash REAL,
            status TEXT DEFAULT 'OPEN'
        )
    ''')
    
    # Sales Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp TEXT NOT NULL,
            total REAL NOT NULL,
            payment_method TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    ''')
    
    # Sale Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price_at_sale REAL,
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized.")

# --- Product Operations ---
def add_product(barcode, name, price, image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (barcode, name, price, image_path) VALUES (?, ?, ?, ?)", (barcode, name, price, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_product_by_barcode(barcode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()
    conn.close()
    if product:
        # Check if tuple has image_path (index 4)
        img = product[4] if len(product) > 4 else None
        return {'id': product[0], 'barcode': product[1], 'name': product[2], 'price': product[3], 'image_path': img}
    return None

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    products = []
    for r in rows:
        img = r[4] if len(r) > 4 else None
        products.append({'id': r[0], 'barcode': r[1], 'name': r[2], 'price': r[3], 'image_path': img})
    return products

def update_product(id, barcode, name, price, image_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if image_path:
            cursor.execute("UPDATE products SET barcode = ?, name = ?, price = ?, image_path = ? WHERE id = ?", (barcode, name, price, image_path, id))
        else:
            cursor.execute("UPDATE products SET barcode = ?, name = ?, price = ? WHERE id = ?", (barcode, name, price, id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_product(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def clear_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    conn.commit()
    conn.close()

# --- Session Operations ---
def create_session(initial_cash):
    conn = get_connection()
    cursor = conn.cursor()
    start_time = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO sessions (start_time, initial_cash, status) VALUES (?, ?, 'OPEN')", (start_time, initial_cash))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_active_session():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE status = 'OPEN' ORDER BY id DESC LIMIT 1")
    session = cursor.fetchone()
    conn.close()
    if session:
        return {'id': session[0], 'start_time': session[1], 'initial_cash': session[3]}
    return None

def close_session(session_id, final_cash):
    conn = get_connection()
    cursor = conn.cursor()
    end_time = datetime.datetime.now().isoformat()
    cursor.execute("UPDATE sessions SET end_time = ?, final_cash = ?, status = 'CLOSED' WHERE id = ?", (end_time, final_cash, session_id))
    conn.commit()
    conn.close()

def update_session_initial_cash(session_id, new_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET initial_cash = ? WHERE id = ?", (new_amount, session_id))
    conn.commit()
    conn.close()

def get_session_sales_total(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total) FROM sales WHERE session_id = ?", (session_id,))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0.0

def get_items_for_sale(sale_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.name, si.quantity, si.price_at_sale, p.image_path, p.barcode
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        WHERE si.sale_id = ?
    ''', (sale_id,))
    rows = cursor.fetchall()
    conn.close()
    items = []
    for r in rows:
        items.append({
            'name': r[0],
            'quantity': r[1],
            'price': r[2],
            'image_path': r[3],
            'barcode': r[4]
        })
    return items

def get_sales_by_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, total, payment_method FROM sales WHERE session_id = ? ORDER BY id DESC", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    sales = []
    for r in rows:
        try:
            dt = datetime.datetime.fromisoformat(r[1])
            ts_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            ts_str = r[1]
            
        sales.append({
            'id': r[0],
            'timestamp': ts_str,
            'total': r[2],
            'payment_method': r[3],
            'items': get_items_for_sale(r[0])
        })
    return sales

def get_all_sales():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, total, payment_method FROM sales ORDER BY id DESC") 
    rows = cursor.fetchall()
    conn.close()
    sales = []
    for r in rows:
        try:
            dt = datetime.datetime.fromisoformat(r[1])
            ts_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            ts_str = r[1]
            
        sales.append({
            'id': r[0],
            'timestamp': ts_str,
            'total': r[2],
            'payment_method': r[3],
            'items': get_items_for_sale(r[0])
        })
    return sales

# --- Sales Operations ---
def record_sale(session_id, items, total, payment_method):
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO sales (session_id, timestamp, total, payment_method) VALUES (?, ?, ?, ?)", 
                   (session_id, timestamp, total, payment_method))
    sale_id = cursor.lastrowid
    
    for item in items:
        cursor.execute("INSERT INTO sale_items (sale_id, product_id, quantity, price_at_sale) VALUES (?, ?, ?, ?)",
                       (sale_id, item['id'], item['quantity'], item['price']))
        
    conn.commit()
    conn.close()
    return sale_id

if __name__ == "__main__":
    init_db()
