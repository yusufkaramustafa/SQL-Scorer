from sqlalchemy import create_engine, text

DB_URL = "sqlite:///test.db" 
engine = create_engine(DB_URL)

def setup_database():
    with engine.connect() as conn:
        # USERS
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            );
        """))

        # ORDERS
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """))

        # PRODUCTS
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            );
        """))

        # ORDER_ITEMS
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
        """))

        # REVIEWS
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                comment TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """))

        # Sample Data
        conn.execute(text("DELETE FROM users;"))
        conn.execute(text("INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 22), ('Charlie', 28);"))
        
        conn.execute(text("DELETE FROM orders;"))
        conn.execute(text("INSERT INTO orders (user_id, order_date, total_price) VALUES (1, '2024-03-20', 60.5);"))

        conn.execute(text("DELETE FROM products;"))
        conn.execute(text("INSERT INTO products (name, price) VALUES ('Widget', 25.0), ('Gadget', 15.5);"))

        conn.execute(text("DELETE FROM order_items;"))
        conn.execute(text("INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 2);"))

        conn.execute(text("DELETE FROM reviews;"))
        conn.execute(text("INSERT INTO reviews (user_id, comment) VALUES (1, 'Great product!');"))

        conn.commit()
        print("Database setup complete with all tables!")

if __name__ == "__main__":
    setup_database()