import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_db, hash_password

class UserManagementWindow:
    def __init__(self, root, parent):
        self.root = root
        self.parent = parent
        self.root.title("User Management")
        self.root.geometry("400x400")

        self.user_tree = ttk.Treeview(root, columns=("ID", "Username", "Role"), show="headings")
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Role", text="Role")
        self.user_tree.column("ID", width=50)
        self.user_tree.column("Username", width=150)
        self.user_tree.column("Role", width=100)
        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit User", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=5)

        self.load_users()

    def load_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        conn = connect_db()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users")
        for row in cursor.fetchall():
            self.user_tree.insert("", tk.END, values=row)
        cursor.close()
        conn.close()

    def add_user(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add User")
        add_win.geometry("300x300")

        tk.Label(add_win, text="Username").pack(pady=5)
        username_entry = tk.Entry(add_win)
        username_entry.pack(pady=5)

        tk.Label(add_win, text="Password").pack(pady=5)
        password_entry = tk.Entry(add_win, show="*")
        password_entry.pack(pady=5)

        tk.Label(add_win, text="Role").pack(pady=5)
        role_var = tk.StringVar(value="user")
        role_combo = ttk.Combobox(add_win, textvariable=role_var, values=["admin", "user"], state="readonly")
        role_combo.pack(pady=5)

        def save_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_var.get()
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required.")
                return
            hashed = hash_password(password)
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, hashed, role)
                )
                conn.commit()
                messagebox.showinfo("Success", "User added!")
                add_win.destroy()
                self.load_users()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            finally:
                cursor.close()
                conn.close()

        tk.Button(add_win, text="Save", command=save_user).pack(pady=10)

    def edit_user(self):
        selected = self.user_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a user.")
            return
        values = self.user_tree.item(selected, 'values')
        user_id = values[0]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit User")
        edit_win.geometry("300x300")

        tk.Label(edit_win, text="Username").pack(pady=5)
        username_entry = tk.Entry(edit_win)
        username_entry.insert(0, values[1])
        username_entry.pack(pady=5)

        tk.Label(edit_win, text="New Password (optional)").pack(pady=5)
        password_entry = tk.Entry(edit_win, show="*")
        password_entry.pack(pady=5)

        tk.Label(edit_win, text="Role").pack(pady=5)
        role_var = tk.StringVar(value=values[2])
        role_combo = ttk.Combobox(edit_win, textvariable=role_var, values=["admin", "user"], state="readonly")
        role_combo.pack(pady=5)

        def update_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            role = role_var.get()
            if not username:
                messagebox.showerror("Error", "Username is required.")
                return
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            if password:
                hashed = hash_password(password)
                cursor.execute(
                    "UPDATE users SET username=%s, password=%s, role=%s WHERE id=%s",
                    (username, hashed, role, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username=%s, role=%s WHERE id=%s",
                    (username, role, user_id)
                )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "User updated!")
            edit_win.destroy()
            self.load_users()

        tk.Button(edit_win, text="Update", command=update_user).pack(pady=10)

    def delete_user(self):
        selected = self.user_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a user.")
            return
        values = self.user_tree.item(selected, 'values')
        if values[1] == self.parent.username:
            messagebox.showerror("Error", "Cannot delete yourself.")
            return
        if messagebox.askyesno("Confirm", "Delete this user?"):
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id=%s", (values[0],))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Success", "User deleted!")
            self.load_users()
