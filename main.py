import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import hashlib
import os

# ------------------- Database Settings -------------------
DB_CONFIG = {
    'user': 'test',
    'password': 'Test1234!',
    'host': 'localhost',
    'database': 'jollibee_inventory',
    'ssl_disabled': True
}

def connect_db():
    """Establish and return a MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    """
    Initialize the database and tables if they do not exist.
    Also ensure a 'role' column in users for role-based access.
    """
    conn = connect_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')

    # Add role column if it doesn't exist
    # MySQL doesn't have "IF NOT EXISTS" for ALTER, so we try/catch.
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'user'")
    except:
        pass  # Column already exists

    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            stock INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------- SignUp Window -------------------
class SignUpWindow:
    """Sign up window for new user registration with optional role selection."""
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Up")
        self.root.geometry("300x250")

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(root, text="Confirm Password").pack(pady=5)
        self.confirm_entry = tk.Entry(root, show="*")
        self.confirm_entry.pack(pady=5)

        # Role selection (admin or user)
        tk.Label(root, text="Role").pack(pady=5)
        self.role_var = tk.StringVar(value="user")
        self.role_combo = ttk.Combobox(root, textvariable=self.role_var, values=["admin", "user"], state="readonly")
        self.role_combo.pack(pady=5)

        tk.Button(root, text="Sign Up", command=self.signup).pack(pady=10)

    def signup(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        hashed = hash_password(password)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed, role)
            )
            conn.commit()
            cursor.close()
            conn.close()

            # Show success, close this window
            messagebox.showinfo("Sign Up", "User created successfully!")
            self.root.destroy()

            # After sign-up success, open the inventory directly (or go back to login if you prefer)
            # Here, we’ll open the main inventory. If you want to go back to login, create a new LoginWindow.
            main_window = tk.Tk()
            InventoryApp(main_window, user_role=role, username=username)
            main_window.mainloop()

        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        except Exception as err:
            messagebox.showerror("Error", f"Error: {err}")

# ------------------- Login Window -------------------
class LoginWindow:
    """Login window for user authentication and sign up."""
    def __init__(self, root):
        self.root = root
        self.root.title("Jollibee Inventory - Login")
        self.root.geometry("300x200")

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Login", command=self.login).pack(pady=5)
        tk.Button(root, text="Sign Up", command=self.go_to_signup).pack(pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        hashed = hash_password(password)

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter username and password.")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, hashed))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            user_role = result[0]  # e.g., 'admin' or 'user'
            messagebox.showinfo("Login", "Login successful!")

            # Close login window
            self.root.destroy()

            # Open main inventory
            main_window = tk.Tk()
            InventoryApp(main_window, user_role=user_role, username=username)
            main_window.mainloop()
        else:
            messagebox.showerror("Login", "Invalid credentials")

    def go_to_signup(self):
        # Close login window
        self.root.destroy()

        # Open Sign Up window
        signup_root = tk.Tk()
        SignUpWindow(signup_root)
        signup_root.mainloop()

# ------------------- Inventory Application -------------------
class InventoryApp:
    """Main application window for inventory management with role-based access."""
    def __init__(self, root, user_role="user", username=""):
        self.root = root
        self.root.title(f"Jollibee Inventory Management - Logged in as {username} ({user_role})")
        self.root.geometry("700x450")

        self.user_role = user_role
        self.username = username

        # Search bar
        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search by Name: ").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="Search", command=self.search_products).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=self.load_products).pack(side=tk.LEFT, padx=5)

        # Treeview to display products
        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Stock", "Price"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Price", text="Price")
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("Stock", width=80)
        self.tree.column("Price", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Button panel
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.btn_add = tk.Button(btn_frame, text="Add Product", command=self.add_product)
        self.btn_add.grid(row=0, column=0, padx=5)

        self.btn_modify = tk.Button(btn_frame, text="Modify Product", command=self.modify_product)
        self.btn_modify.grid(row=0, column=1, padx=5)

        self.btn_remove = tk.Button(btn_frame, text="Remove Product", command=self.remove_product)
        self.btn_remove.grid(row=0, column=2, padx=5)

        tk.Button(btn_frame, text="Refresh", command=self.load_products).grid(row=0, column=3, padx=5)

        # Summary label
        self.summary_label = tk.Label(root, text="", font=("Arial", 10, "bold"))
        self.summary_label.pack(pady=5)

        # Adjust access based on role
        self.configure_role_access()

        # Load products
        self.load_products()

    def configure_role_access(self):
        """Enable/disable certain buttons depending on the user role."""
        if self.user_role == "user":
            # Disable product management
            self.btn_add.config(state=tk.DISABLED)
            self.btn_modify.config(state=tk.DISABLED)
            self.btn_remove.config(state=tk.DISABLED)

    def load_products(self):
        """Load all products from the database and display in the treeview."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

        cursor.close()
        conn.close()

        # Update summary
        self.update_summary()

    def search_products(self):
        """Search products by name."""
        search_text = self.search_var.get().strip()

        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE name LIKE %s"
        cursor.execute(query, (f"%{search_text}%",))
        rows = cursor.fetchall()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

        cursor.close()
        conn.close()

        self.update_summary()

    def update_summary(self):
        """Show total products, total stock, and total inventory value."""
        conn = connect_db()
        cursor = conn.cursor()

        # Count total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        # Sum stock and total value
        cursor.execute("SELECT IFNULL(SUM(stock), 0), IFNULL(SUM(stock * price), 0) FROM products")
        stock_sum, value_sum = cursor.fetchone()

        cursor.close()
        conn.close()

        self.summary_label.config(
            text=f"Total Products: {total_products} | Total Stock: {stock_sum} | Total Value: {value_sum:.2f}"
        )

    def add_product(self):
        """Open a window to add a new product."""
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Product")
        add_win.geometry("300x250")

        tk.Label(add_win, text="Product Name").pack(pady=5)
        name_entry = tk.Entry(add_win)
        name_entry.pack(pady=5)

        tk.Label(add_win, text="Stock").pack(pady=5)
        stock_entry = tk.Entry(add_win)
        stock_entry.pack(pady=5)

        tk.Label(add_win, text="Price").pack(pady=5)
        price_entry = tk.Entry(add_win)
        price_entry.pack(pady=5)

        def save_product():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Product name cannot be empty.")
                return
            try:
                stock = int(stock_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid stock or price value.")
                return

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (name, stock, price) VALUES (%s, %s, %s)",
                (name, stock, price)
            )
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Product added successfully!")
            add_win.destroy()
            self.load_products()

        tk.Button(add_win, text="Save", command=save_product).pack(pady=10)

    def modify_product(self):
        """Open a window to modify the selected product."""
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a product to modify.")
            return

        values = self.tree.item(selected, 'values')
        product_id = values[0]

        modify_win = tk.Toplevel(self.root)
        modify_win.title("Modify Product")
        modify_win.geometry("300x250")

        tk.Label(modify_win, text="Product Name").pack(pady=5)
        name_entry = tk.Entry(modify_win)
        name_entry.insert(0, values[1])
        name_entry.pack(pady=5)

        tk.Label(modify_win, text="Stock").pack(pady=5)
        stock_entry = tk.Entry(modify_win)
        stock_entry.insert(0, values[2])
        stock_entry.pack(pady=5)

        tk.Label(modify_win, text="Price").pack(pady=5)
        price_entry = tk.Entry(modify_win)
        price_entry.insert(0, values[3])
        price_entry.pack(pady=5)

        def update_product():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Product name cannot be empty.")
                return
            try:
                stock = int(stock_entry.get())
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid stock or price value.")
                return

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET name=%s, stock=%s, price=%s WHERE id=%s",
                (name, stock, price, product_id)
            )
            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", "Product updated successfully!")
            modify_win.destroy()
            self.load_products()

        tk.Button(modify_win, text="Update", command=update_product).pack(pady=10)

    def remove_product(self):
        """Remove the selected product from the database."""
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a product to remove.")
            return

        values = self.tree.item(selected, 'values')
        product_id = values[0]

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove this product?")
        if confirm:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "Product removed successfully!")
            self.load_products()

# ------------------- Main Execution -------------------
if __name__ == "__main__":
    init_db()  # Initialize database and tables

    # Start with the Login window
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
