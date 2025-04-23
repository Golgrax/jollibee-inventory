import mysql.connector
import hashlib
from tkinter import messagebox

DB_CONFIG = {
    'user': 'test',
    'password': 'Test1234!',
    'host': 'localhost',
    'database': 'jollibee_inventory',
    'ssl_disabled': True
}

def connect_db():
    """Establish and return a MySQL connection with error handling."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

def init_db():
    """Initialize the database with users, categories, and products tables."""
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'user'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category_id INT,
            stock INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()
