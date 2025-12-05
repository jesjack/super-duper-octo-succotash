import database
import sqlite3

def seed_products():
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Clear existing products to avoid duplicates during testing
    cursor.execute("DELETE FROM products")
    
    products = [
        ("123456", "Test Product A", 10.50),
        ("7501055311868", "Coca Cola 600ml", 18.00),
        ("7501000111208", "Sabritas Original", 15.00),
        ("000001", "Generic Item 1", 5.00),
        ("000002", "Generic Item 2", 100.00),
    ]
    
    print("Seeding products...")
    for barcode, name, price in products:
        try:
            cursor.execute("INSERT INTO products (barcode, name, price) VALUES (?, ?, ?)", (barcode, name, price))
            print(f"Added: {name} ({barcode}) - ${price}")
        except sqlite3.IntegrityError:
            print(f"Skipped (Duplicate): {name}")
            
    conn.commit()
    conn.close()
    print("Seeding complete.")

if __name__ == "__main__":
    database.init_db()
    seed_products()
