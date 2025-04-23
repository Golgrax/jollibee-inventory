import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_db, hash_password
from inventory import InventoryApp

class SignUpWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sign Up")
        self.root.geometry("300x300")

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(root, text="Confirm Password").pack(pady=5)
        self.confirm_entry = tk.Entry(root, show="*")
        self.confirm_entry.pack(pady=5)

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

        if not username or not password or not confirm:
            messagebox.showerror("Error", "All fields are required.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        hashed = hash_password(password)
        try:
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed, role)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "User created successfully!")
            self.root.destroy()
            main_window = tk.Tk()
            InventoryApp(main_window, user_role=role, username=username)
            main_window.mainloop()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
        except Exception as err:
            messagebox.showerror("Error", f"Error: {err}")
