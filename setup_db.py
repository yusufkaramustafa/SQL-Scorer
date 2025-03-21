from sqlalchemy import create_engine, text

DB_URL = "sqlite:///test.db" 
engine = create_engine(DB_URL)

def setup_database():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """))

        # Insert sample data
        conn.execute(text("INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 22), ('Charlie', 28);"))
        conn.execute(text("INSERT INTO orders (user_id, order_date, total_price) VALUES (1, '2024-03-20', 60.5);"))
        
        conn.commit()
        print("Database setup complete!")

if __name__ == "__main__":
    setup_database()