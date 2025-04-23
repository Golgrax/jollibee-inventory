import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_db, hash_password
from inventory import InventoryApp
from signup import SignUpWindow

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Jollibee Inventory - Login")
        self.root.geometry("300x300")

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
            messagebox.showerror("Error", "Please enter username and password.")
            return

        conn = connect_db()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username=%s AND password=%s", (username, hashed))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            user_id, user_role = result
            messagebox.showinfo("Login", "Login successful!")
            self.root.destroy()
            main_window = tk.Tk()
            InventoryApp(main_window, user_role=user_role, username=username, user_id=user_id)
            main_window.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def go_to_signup(self):
        self.root.destroy()
        signup_root = tk.Tk()
        SignUpWindow(signup_root)
        signup_root.mainloop()
