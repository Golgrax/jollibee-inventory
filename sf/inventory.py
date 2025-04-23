import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import mysql.connector
from database import connect_db, hash_password
from user_management import UserManagementWindow

class InventoryApp:
    def __init__(self, root, user_role="user", username="", user_id=None):
        self.root = root
        self.user_role = user_role
        self.username = username
        self.user_id = user_id
        self.root.title(f"Jollibee Inventory - {username} ({user_role})")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        # Color scheme (Jollibee theme)
        self.primary_color = "#FF0000"  # Red
        self.secondary_color = "#FFFFFF"  # White
        self.accent_colors = ["#ADD8E6", "#90EE90", "#FFA500", "#9370DB"]
        self.text_color = "#333333"  # Dark Gray

        # Theme settings
        self.current_theme = "light"
        self.themes = {
            "light": {"bg": "#FFFFFF", "fg": "#333333", "btn_bg": "#FF0000", "btn_fg": "#FFFFFF"},
            "dark": {"bg": "#333333", "fg": "#FFFFFF", "btn_bg": "#FF5555", "btn_fg": "#000000"}
        }

        # Font
        self.font = ("Helvetica", 12)

        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", font=self.font, rowheight=25)
        self.style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
        self.style.map("Treeview", background=[("selected", "#FFC107")])

        # Header
        self.header_frame = tk.Frame(self.root, bg=self.primary_color)
        self.header_frame.pack(fill="x")
        tk.Label(self.header_frame, text="Jollibee Inventory System", font=("Helvetica", 16, "bold"),
                bg=self.primary_color, fg=self.secondary_color).pack(side="left", padx=10, pady=10)
        user_frame = tk.Frame(self.header_frame, bg=self.primary_color)
        user_frame.pack(side="right", padx=10)
        tk.Label(user_frame, text=f"👤 {username}", font=self.font, bg=self.primary_color,
                fg=self.secondary_color).pack(side="left")
        bell_label = tk.Label(user_frame, text="🔔", font=self.font, bg=self.primary_color,
                fg=self.secondary_color, cursor="hand2")
        bell_label.pack(side="left", padx=5)
        bell_label.bind("<Button-1>", self.show_notifications)

        # Sidebar
        self.sidebar_frame = tk.Frame(self.root, bg="#F0F0F0", width=200)
        self.sidebar_frame.pack(side="left", fill="y")
        nav_items = [("Dashboard", "🏠"), ("Products", "📦"), ("Categories", "📏"),
                    ("Users", "👥"), ("Reports", "📊"), ("Activity Log", "📝"), ("Settings", "⚙️")]
        for text, icon in nav_items:
            btn = tk.Button(self.sidebar_frame, text=f"{icon} {text}", font=self.font, bg="#F0F0F0",
                           fg=self.text_color, relief="flat", anchor="w",
                           command=lambda t=text: self.switch_view(t))
            btn.pack(fill="x", padx=10, pady=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#FFC1CC"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#F0F0F0"))

        # Main content frame
        self.main_frame = tk.Frame(self.root, bg=self.secondary_color)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Helvetica", 10),
                                    bg=self.secondary_color, fg=self.text_color, anchor="w")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

        # Notifications list
        self.notifications = []

        # Initial view
        self.display_dashboard()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])
        self.main_frame.configure(bg=theme["bg"])
        self.header_frame.configure(bg=self.primary_color)
        self.sidebar_frame.configure(bg="#F0F0F0" if self.current_theme == "light" else "#444444")
        self.status_label.configure(bg=theme["bg"], fg=theme["fg"])
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=theme["btn_bg"], fg=theme["btn_fg"])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=theme["bg"])

    def switch_view(self, view):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        if view == "Dashboard":
            self.display_dashboard()
        elif view == "Products":
            self.display_products()
        elif view == "Categories":
            self.display_categories()
        elif view == "Users":
            self.display_users()
        elif view == "Reports":
            self.display_reports()
        elif view == "Activity Log":
            self.display_activity_log()
        elif view == "Settings":
            self.display_settings()

    def display_dashboard(self):
        tk.Label(self.main_frame, text="Dashboard", font=("Helvetica", 18, "bold"),
                bg=self.secondary_color).pack(anchor="w", pady=10)

        metrics_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        metrics_frame.pack(fill="x", pady=10)
        metrics = self.get_dashboard_metrics()
        for i, (title, value, subtitle) in enumerate(metrics):
            card = tk.Frame(metrics_frame, bg=self.accent_colors[i % len(self.accent_colors)],
                           padx=15, pady=15, relief="raised", bd=2)
            card.pack(side="left", padx=10, fill="x", expand=True)
            tk.Label(card, text=title, font=("Helvetica", 10), bg=card["bg"]).pack()
            tk.Label(card, text=value, font=("Helvetica", 18, "bold"), bg=card["bg"]).pack()
            tk.Label(card, text=subtitle, font=("Helvetica", 8), bg=card["bg"],
                    fg="green" if "increase" in subtitle else self.text_color).pack()

        table_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        table_frame.pack(fill="both", expand=True, pady=10)
        table_header = tk.Frame(table_frame, bg=self.secondary_color)
        table_header.pack(fill="x")
        tk.Label(table_header, text="Recent Products", font=("Helvetica", 14, "bold"),
                bg=self.secondary_color).pack(side="left")
        view_all = tk.Label(table_header, text="View All", font=self.font, fg="blue",
                           cursor="hand2", bg=self.secondary_color)
        view_all.pack(side="right")
        view_all.bind("<Button-1>", lambda e: self.switch_view("Products"))

        self.recent_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Category", "Stock", "Price"),
                                       show="headings")
        for col in self.recent_tree["columns"]:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=120, anchor="center")
        self.recent_tree.pack(fill="both", expand=True)
        self.load_recent_products()

    def display_products(self):
        search_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        search_frame.pack(fill=tk.X, pady=10)

        tk.Label(search_frame, text="Category:", font=self.font, bg=self.secondary_color).pack(side=tk.LEFT, padx=5)
        self.category_filter_var = tk.StringVar()
        self.category_filter_combo = ttk.Combobox(search_frame, textvariable=self.category_filter_var, font=self.font)
        self.category_filter_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(search_frame, text="Search:", font=self.font, bg=self.secondary_color).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=self.font)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(search_frame, text="Min Price:", font=self.font, bg=self.secondary_color).pack(side=tk.LEFT, padx=5)
        self.min_price_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.min_price_var, width=10, font=self.font).pack(side=tk.LEFT, padx=5)

        tk.Label(search_frame, text="Max Price:", font=self.font, bg=self.secondary_color).pack(side=tk.LEFT, padx=5)
        self.max_price_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.max_price_var, width=10, font=self.font).pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="Search", command=self.search_products, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=self.load_products, bg="#FFC107",
                 fg=self.text_color, font=self.font).pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Category", "Stock", "Price"),
                                show="headings")
        self.tree.heading("ID", text="ID", command=lambda: self.sort_column("ID", False))
        self.tree.heading("Name", text="Name", command=lambda: self.sort_column("Name", False))
        self.tree.heading("Category", text="Category", command=lambda: self.sort_column("Category", False))
        self.tree.heading("Stock", text="Stock", command=lambda: self.sort_column("Stock", False))
        self.tree.heading("Price", text="Price", command=lambda: self.sort_column("Price", False))
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=200)
        self.tree.column("Category", width=150)
        self.tree.column("Stock", width=80, anchor="center")
        self.tree.column("Price", width=80, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        btn_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        btn_frame.pack(fill=tk.X, pady=10)
        self.btn_add = tk.Button(btn_frame, text="Add", command=self.open_add_product_window, bg=self.primary_color,
                                fg=self.secondary_color, font=self.font)
        self.btn_add.pack(side=tk.LEFT, padx=5)
        self.btn_modify = tk.Button(btn_frame, text="Modify", command=self.open_modify_product_window, bg=self.primary_color,
                                   fg=self.secondary_color, font=self.font)
        self.btn_modify.pack(side=tk.LEFT, padx=5)
        self.btn_remove = tk.Button(btn_frame, text="Remove", command=self.remove_product, bg=self.primary_color,
                                   fg=self.secondary_color, font=self.font)
        self.btn_remove.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_products, bg="#FFC107",
                 fg=self.text_color, font=self.font).pack(side=tk.LEFT, padx=5)

        self.summary_label = tk.Label(self.main_frame, text="", font=("Helvetica", 14, "bold"),
                                     bg=self.secondary_color, fg=self.text_color)
        self.summary_label.pack(fill=tk.X, pady=10)

        self.configure_role_access()
        self.load_categories()
        self.load_products()

    def display_categories(self):
        tk.Label(self.main_frame, text="Categories", font=("Helvetica", 18, "bold"),
                bg=self.secondary_color).pack(anchor="w", pady=10)

        self.category_tree = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Parent"), show="headings")
        self.category_tree.heading("ID", text="ID")
        self.category_tree.heading("Name", text="Name")
        self.category_tree.heading("Parent", text="Parent Category")
        self.category_tree.column("ID", width=50)
        self.category_tree.column("Name", width=200)
        self.category_tree.column("Parent", width=150)
        self.category_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        btn_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Add", command=self.open_add_category_window, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit", command=self.open_edit_category_window, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_category, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)

        self.load_categories_list()

    def display_users(self):
        if self.user_role != "admin":
            tk.Label(self.main_frame, text="Access Denied", font=("Helvetica", 18, "bold"),
                    bg=self.secondary_color).pack(pady=20)
            return

        tk.Label(self.main_frame, text="Users", font=("Helvetica", 18, "bold"),
                bg=self.secondary_color).pack(anchor="w", pady=10)

        self.user_tree = ttk.Treeview(self.main_frame, columns=("ID", "Username", "Role"), show="headings")
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Role", text="Role")
        self.user_tree.column("ID", width=50)
        self.user_tree.column("Username", width=150)
        self.user_tree.column("Role", width=100)
        self.user_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        btn_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Add User", command=self.open_add_user_window, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit User", command=self.open_edit_user_window, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete User", command=self.delete_user, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)

        self.load_users()

    def display_reports(self):
        tk.Label(self.main_frame, text="Reports", font=("Helvetica", 18, "bold"),
                bg=self.secondary_color).pack(anchor="w", pady=10)

        report_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        report_frame.pack(fill=tk.X, pady=5)
        report_types = ["Low Stock", "High Stock", "Most Expensive", "Least Expensive", "Category Summary"]
        for report in report_types:
            tk.Button(report_frame, text=report, command=lambda r=report: self.load_report(r),
                     bg=self.primary_color, fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)

        self.report_tree = ttk.Treeview(self.main_frame, columns=("ID", "Name", "Stock", "Price"), show="headings")
        self.report_tree.heading("ID", text="ID")
        self.report_tree.heading("Name", text="Name")
        self.report_tree.heading("Stock", text="Stock")
        self.report_tree.heading("Price", text="Price")
        self.report_tree.column("ID", width=50)
        self.report_tree.column("Name", width=200)
        self.report_tree.column("Stock", width=100)
        self.report_tree.column("Price", width=100)
        self.report_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        btn_frame = tk.Frame(self.main_frame, bg=self.secondary_color)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Export Report", command=self.export_report, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(side=tk.LEFT, padx=5)

        self.load_report("Low Stock")

    def display_activity_log(self):
        tk.Label(self.main_frame, text="Activity Log", font=("Helvetica", 18, "bold"),
                bg=self.secondary_color).pack(anchor="w", pady=10)

        self.activity_tree = ttk.Treeview(self.main_frame, columns=("Timestamp", "User", "Action", "Details"),
                                         show="headings")
        self.activity_tree.heading("Timestamp", text="Timestamp")
        self.activity_tree.heading("User", text="User")
        self.activity_tree.heading("Action", text="Action")
        self.activity_tree.heading("Details", text="Details")
        self.activity_tree.column("Timestamp", width=150)
        self.activity_tree.column("User", width=100)
        self.activity_tree.column("Action", width=100)
        self.activity_tree.column("Details", width=250)
        self.activity_tree.pack(fill=tk.BOTH, expand=True, pady=10)

        tk.Button(self.main_frame, text="Refresh", command=self.load_activity_log, bg=self.primary_color,
                 fg=self.secondary_color, font=self.font).pack(pady=5)

        self.load_activity_log()

    def display_settings(self):
        tk.Label(self.main_frame, text="Settings", font=("Helvetica", 18, "bold"),
                bg=self.secondary_color).pack(anchor="w", pady=10)

        tk.Button(self.main_frame, text="Change Password", command=self.open_change_password_window,
                 bg=self.primary_color, fg=self.secondary_color, font=self.font).pack(pady=5)
        tk.Button(self.main_frame, text="Backup Database", command=self.backup_database,
                 bg=self.primary_color, fg=self.secondary_color, font=self.font).pack(pady=5)
        tk.Button(self.main_frame, text="Restore Database", command=self.restore_database,
                 bg=self.primary_color, fg=self.secondary_color, font=self.font).pack(pady=5)

        tk.Label(self.main_frame, text="Theme", font=("Helvetica", 14, "bold"),
                bg=self.secondary_color).pack(anchor="w", pady=5)
        theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(self.main_frame, textvariable=theme_var, values=list(self.themes.keys()),
                                  state="readonly")
        theme_combo.pack(pady=5)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self.change_theme(theme_var.get()))

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = connect_db()
        if conn is None:
            self.status_var.set("Database connection failed.")
            return
        try:
            cursor = conn.cursor()
            category = self.category_filter_var.get()
            if category == "All":
                cursor.execute("SELECT p.id, p.name, c.name, p.stock, p.price FROM products p LEFT JOIN categories c ON p.category_id = c.id")
            else:
                cursor.execute("SELECT p.id, p.name, c.name, p.stock, p.price FROM products p JOIN categories c ON p.category_id = c.id WHERE c.name=%s", (category,))
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=(row[0], row[1], row[2] or "", row[3], f"P{row[4]:.2f}"))
        except mysql.connector.Error as e:
            self.status_var.set(f"Error loading products: {str(e)}")
        finally:
            cursor.close()
            conn.close()
        self.update_summary()

    def search_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = connect_db()
        if conn is None:
            self.status_var.set("Database connection failed.")
            return
        try:
            cursor = conn.cursor()
            search_term = f"%{self.search_var.get()}%"
            category = self.category_filter_var.get()
            min_price = self.min_price_var.get() or "0"
            max_price = self.max_price_var.get() or "9999999"
            try:
                min_price = float(min_price)
                max_price = float(max_price)
            except ValueError:
                messagebox.showerror("Error", "Invalid price range.")
                return

            query = """
                SELECT p.id, p.name, c.name, p.stock, p.price
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.name LIKE %s AND p.price BETWEEN %s AND %s
            """
            params = [search_term, min_price, max_price]
            if category != "All":
                query += " AND c.name = %s"
                params.append(category)

            cursor.execute(query, params)
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=(row[0], row[1], row[2] or "", row[3], f"P{row[4]:.2f}"))
        except mysql.connector.Error as e:
            self.status_var.set(f"Error searching products: {str(e)}")
        finally:
            cursor.close()
            conn.close()
        self.update_summary()

    def load_categories_list(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT c.id, c.name, p.name FROM categories c LEFT JOIN categories p ON c.parent_id = p.id")
            for row in cursor.fetchall():
                self.category_tree.insert("", tk.END, values=(row[0], row[1], row[2] or "None"))
        except mysql.connector.Error as e:
            self.status_var.set(f"Error loading categories: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def open_add_category_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Category")
        add_win.geometry("300x200")

        tk.Label(add_win, text="Category Name").pack(pady=5)
        name_entry = tk.Entry(add_win)
        name_entry.pack(pady=5)

        tk.Label(add_win, text="Parent Category").pack(pady=5)
        parent_var = tk.StringVar()
        categories = self.get_category_dict()
        category_names = ["None"] + list(categories.keys())
        parent_combo = ttk.Combobox(add_win, textvariable=parent_var, values=category_names, state="readonly")
        parent_combo.pack(pady=5)
        parent_combo.set("None")

        def save_category():
            name = name_entry.get().strip()
            parent = parent_var.get()
            if not name:
                messagebox.showerror("Error", "Category name is required.")
                return
            conn = connect_db()
            if conn is None:
                return
            try:
                cursor = conn.cursor()
                parent_id = None if parent == "None" else categories[parent]
                cursor.execute("INSERT INTO categories (name, parent_id) VALUES (%s, %s)", (name, parent_id))
                conn.commit()
                self.log_activity("Add Category", f"Added category: {name}")
                messagebox.showinfo("Success", "Category added!")
                add_win.destroy()
                self.load_categories_list()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Category name already exists.")
            except mysql.connector.Error as e:
                self.status_var.set(f"Error adding category: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        tk.Button(add_win, text="Save", command=save_category).pack(pady=10)

    def open_edit_category_window(self):
        selected = self.category_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a category.")
            return
        values = self.category_tree.item(selected, 'values')
        category_id = values[0]

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Category")
        edit_win.geometry("300x200")

        tk.Label(edit_win, text="Category Name").pack(pady=5)
        name_entry = tk.Entry(edit_win)
        name_entry.insert(0, values[1])
        name_entry.pack(pady=5)

        tk.Label(edit_win, text="Parent Category").pack(pady=5)
        parent_var = tk.StringVar(value=values[2])
        categories = self.get_category_dict()
        category_names = ["None"] + list(categories.keys())
        parent_combo = ttk.Combobox(edit_win, textvariable=parent_var, values=category_names, state="readonly")
        parent_combo.pack(pady=5)

        def update_category():
            new_name = name_entry.get().strip()
            parent = parent_var.get()
            if not new_name:
                messagebox.showerror("Error", "Category name is required.")
                return
            conn = connect_db()
            if conn is None:
                return
            try:
                cursor = conn.cursor()
                parent_id = None if parent == "None" else categories[parent]
                cursor.execute("UPDATE categories SET name=%s, parent_id=%s WHERE id=%s",
                              (new_name, parent_id, category_id))
                conn.commit()
                self.log_activity("Edit Category", f"Updated category: {new_name}")
                messagebox.showinfo("Success", "Category updated!")
                edit_win.destroy()
                self.load_categories_list()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Category name already exists.")
            except mysql.connector.Error as e:
                self.status_var.set(f"Error updating category: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        tk.Button(edit_win, text="Update", command=update_category).pack(pady=10)

    def delete_category(self):
        selected = self.category_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a category.")
            return
        values = self.category_tree.item(selected, 'values')
        category_id = values[0]

        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products WHERE category_id=%s", (category_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                messagebox.showerror("Error", "Cannot delete category with associated products.")
                return
            cursor.execute("SELECT COUNT(*) FROM categories WHERE parent_id=%s", (category_id,))
            sub_count = cursor.fetchone()[0]
            if sub_count > 0:
                messagebox.showerror("Error", "Cannot delete category with subcategories.")
                return

            if messagebox.askyesno("Confirm", "Delete this category?"):
                cursor.execute("DELETE FROM categories WHERE id=%s", (category_id,))
                conn.commit()
                self.log_activity("Delete Category", f"Deleted category: {values[1]}")
                messagebox.showinfo("Success", "Category deleted!")
                self.load_categories_list()
        except mysql.connector.Error as e:
            self.status_var.set(f"Error deleting category: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def load_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users")
            for row in cursor.fetchall():
                self.user_tree.insert("", tk.END, values=row)
        except mysql.connector.Error as e:
            self.status_var.set(f"Error loading users: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def open_add_user_window(self):
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
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, hashed, role)
                )
                conn.commit()
                self.log_activity("Add User", f"Added user: {username}")
                messagebox.showinfo("Success", "User added!")
                add_win.destroy()
                self.load_users()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            except mysql.connector.Error as e:
                self.status_var.set(f"Error adding user: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        tk.Button(add_win, text="Save", command=save_user).pack(pady=10)

    def open_edit_user_window(self):
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
            try:
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
                self.log_activity("Edit User", f"Updated user: {username}")
                messagebox.showinfo("Success", "User updated!")
                edit_win.destroy()
                self.load_users()
            except mysql.connector.Error as e:
                self.status_var.set(f"Error updating user: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        tk.Button(edit_win, text="Update", command=update_user).pack(pady=10)

    def delete_user(self):
        selected = self.user_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a user.")
            return
        values = self.user_tree.item(selected, 'values')
        if values[1] == self.username:
            messagebox.showerror("Error", "Cannot delete yourself.")
            return
        if messagebox.askyesno("Confirm", "Delete this user?"):
            conn = connect_db()
            if conn is None:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id=%s", (values[0],))
                conn.commit()
                self.log_activity("Delete User", f"Deleted user: {values[1]}")
                messagebox.showinfo("Success", "User deleted!")
                self.load_users()
            except mysql.connector.Error as e:
                self.status_var.set(f"Error deleting user: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def load_report(self, report_type):
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        conn = connect_db()
        if conn is None:
            self.status_var.set("Database connection failed.")
            return
        try:
            cursor = conn.cursor()
            if report_type == "Low Stock":
                cursor.execute("SELECT id, name, stock, price FROM products WHERE stock < 10")
            elif report_type == "High Stock":
                cursor.execute("SELECT id, name, stock, price FROM products WHERE stock > 100")
            elif report_type == "Most Expensive":
                cursor.execute("SELECT id, name, stock, price FROM products ORDER BY price DESC LIMIT 5")
            elif report_type == "Least Expensive":
                cursor.execute("SELECT id, name, stock, price FROM products ORDER BY price ASC LIMIT 5")
            elif report_type == "Category Summary":
                cursor.execute("SELECT c.name, SUM(p.stock), AVG(p.price) FROM products p JOIN categories c ON p.category_id = c.id GROUP BY c.name")
                self.report_tree["columns"] = ("Category", "Total Stock", "Avg Price")
                self.report_tree.heading("Category", text="Category")
                self.report_tree.heading("Total Stock", text="Total Stock")
                self.report_tree.heading("Avg Price", text="Avg Price")
                self.report_tree.column("Category", width=200)
                self.report_tree.column("Total Stock", width=100)
                self.report_tree.column("Avg Price", width=100)
            for row in cursor.fetchall():
                if report_type == "Category Summary":
                    self.report_tree.insert("", tk.END, values=(row[0], row[1], f"P{row[2]:.2f}"))
                else:
                    self.report_tree.insert("", tk.END, values=(row[0], row[1], row[2], f"P{row[3]:.2f}"))
        except mysql.connector.Error as e:
            self.status_var.set(f"Error loading report: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def export_report(self):
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            report_data = []
            for item in self.report_tree.get_children():
                report_data.append(self.report_tree.item(item, 'values'))
            if not report_data:
                messagebox.showinfo("Export", "No data to export.")
                return
            headers = [self.report_tree.heading(col)["text"] for col in self.report_tree["columns"]]
            report_text = f"Report\n{' | '.join(headers)}\n" + "\n".join(" | ".join(map(str, row)) for row in report_data)
            export_win = tk.Toplevel(self.root)
            export_win.title("Export Report")
            export_win.geometry("400x300")
            text_widget = tk.Text(export_win, height=15, width=50)
            text_widget.insert(tk.END, report_text)
            text_widget.pack(pady=10)
            messagebox.showinfo("Export", "Report generated. Copy the text above as needed.")
        except mysql.connector.Error as e:
            self.status_var.set(f"Error exporting report: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def load_activity_log(self):
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, username, action, details FROM activity_log JOIN users ON activity_log.user_id = users.id ORDER BY timestamp DESC")
            for row in cursor.fetchall():
                self.activity_tree.insert("", tk.END, values=row)
        except mysql.connector.Error as e:
            self.status_var.set(f"Error loading activity log: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def log_activity(self, action, details):
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
                          (self.user_id, action, details))
            conn.commit()
        except mysql.connector.Error as e:
            self.status_var.set(f"Error logging activity: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def backup_database(self):
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            backup_data = {}
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                backup_data[table] = cursor.fetchall()
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                backup_data[f"{table}_columns"] = [row[0] for row in cursor.fetchall()]
            import json
            with open("inventory_backup.json", "w") as f:
                json.dump(backup_data, f)
            messagebox.showinfo("Success", "Database backed up to 'inventory_backup.json'.")
        except Exception as e:
            self.status_var.set(f"Error during backup: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def restore_database(self):
        if not messagebox.askyesno("Confirm", "This will overwrite existing data. Proceed?"):
            return
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            import json
            with open("inventory_backup.json", "r") as f:
                backup_data = json.load(f)
            for table in [t for t in backup_data.keys() if not t.endswith("_columns")]:
                cursor.execute(f"TRUNCATE TABLE {table}")
                columns = backup_data[f"{table}_columns"]
                placeholders = ",".join(["%s"] * len(columns))
                cursor.executemany(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
                                 backup_data[table])
            conn.commit()
            messagebox.showinfo("Success", "Database restored from 'inventory_backup.json'.")
            self.switch_view("Dashboard")
        except Exception as e:
            self.status_var.set(f"Error during restore: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def open_change_password_window(self):
        change_win = tk.Toplevel(self.root)
        change_win.title("Change Password")
        change_win.geometry("300x200")

        tk.Label(change_win, text="Old Password").pack(pady=5)
        old_pass_entry = tk.Entry(change_win, show="*")
        old_pass_entry.pack(pady=5)

        tk.Label(change_win, text="New Password").pack(pady=5)
        new_pass_entry = tk.Entry(change_win, show="*")
        new_pass_entry.pack(pady=5)

        tk.Label(change_win, text="Confirm New Password").pack(pady=5)
        confirm_pass_entry = tk.Entry(change_win, show="*")
        confirm_pass_entry.pack(pady=5)

        def save_new_password():
            old_pass = old_pass_entry.get().strip()
            new_pass = new_pass_entry.get().strip()
            confirm_pass = confirm_pass_entry.get().strip()

            if not all([old_pass, new_pass, confirm_pass]):
                messagebox.showerror("Error", "All fields are required.")
                return

            if new_pass != confirm_pass:
                messagebox.showerror("Error", "New passwords do not match.")
                return

            conn = connect_db()
            if conn is None:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE id=%s", (self.user_id,))
                current_hash = cursor.fetchone()[0]
                if hash_password(old_pass) != current_hash:
                    messagebox.showerror("Error", "Old password is incorrect.")
                    return
                new_hash = hash_password(new_pass)
                cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_hash, self.user_id))
                conn.commit()
                self.log_activity("Change Password", "User changed their password")
                messagebox.showinfo("Success", "Password changed successfully!")
                change_win.destroy()
            except mysql.connector.Error as e:
                self.status_var.set(f"Error changing password: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        tk.Button(change_win, text="Save", command=save_new_password).pack(pady=10)

    def change_theme(self, theme):
        self.current_theme = theme
        self.apply_theme()
        self.switch_view("Settings")

    def get_dashboard_metrics(self):
        conn = connect_db()
        if conn is None:
            return [("Error", "N/A", "Database unavailable")]
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM categories")
            total_categories = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM products WHERE stock < 10")
            low_stock = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            return [
                ("Total Products", str(total_products), "Inventory items"),
                ("Categories", str(total_categories), "Active categories"),
                ("Low Stock", str(low_stock), "Needs attention"),
                ("Total Users", str(total_users), "System users")
            ]
        except mysql.connector.Error as e:
            self.status_var.set(f"Error fetching metrics: {str(e)}")
            return [("Error", "N/A", "Database error")]
        finally:
            cursor.close()
            conn.close()

    def load_recent_products(self):
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, c.name, p.stock, p.price
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.id DESC
                LIMIT 5
            """)
            for row in cursor.fetchall():
                self.recent_tree.insert("", tk.END, values=(row[0], row[1], row[2] or "", row[3], f"P{row[4]:.2f}"))
        except mysql.connector.Error as e:
            self.status_var.set(f"Error loading recent products: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def open_add_product_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Product")
        add_win.geometry("300x300")
        add_win.grab_set()

        tk.Label(add_win, text="Name").pack(pady=5)
        name_entry = tk.Entry(add_win)
        name_entry.pack(pady=5)

        tk.Label(add_win, text="Category").pack(pady=5)
        categories = self.get_category_dict()
        category_names = ["None"] + list(categories.keys())
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(add_win, textvariable=category_var, values=category_names, state="readonly")
        category_combo.pack(pady=5)

        tk.Label(add_win, text="Stock").pack(pady=5)
        stock_entry = tk.Entry(add_win)
        stock_entry.pack(pady=5)

        tk.Label(add_win, text="Price").pack(pady=5)
        price_entry = tk.Entry(add_win)
        price_entry.pack(pady=5)

        def save_product():
            name = name_entry.get().strip()
            category = category_var.get()
            stock = stock_entry.get().strip()
            price = price_entry.get().strip()

            if not all([name, stock, price]):
                messagebox.showerror("Error", "Name, stock, and price are required.")
                return

            try:
                stock = int(stock)
                price = float(price)
            except ValueError:
                messagebox.showerror("Error", "Stock must be an integer and price must be a number.")
                return

            category_id = None if category == "None" else categories.get(category)
            conn = connect_db()
            if conn is None:
                return
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (name, category_id, stock, price) VALUES (%s, %s, %s, %s)",
                    (name, category_id, stock, price)
                )
                conn.commit()
                self.log_activity("Add Product", f"Added product: {name}")
                self.status_var.set("Product added successfully.")
                if stock < 10:
                    self.add_notification(f"Low stock alert: {name} has only {stock} units.", "warning")
                elif stock > 100:
                    self.add_notification(f"High stock notice: {name} has {stock} units.", "info")
                add_win.destroy()
                self.load_products()
                if "Dashboard" in [w.winfo_name() for w in self.main_frame.winfo_children()]:
                    self.load_recent_products()
            except mysql.connector.Error as e:
                self.status_var.set(f"Error adding product: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        tk.Button(add_win, text="Save", command=save_product).pack(pady=10)

    def open_modify_product_window(self):
        product_id = self.get_selected_product()
        if product_id is None:
            return

        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name, category_id, stock, price FROM products WHERE id=%s", (product_id,))
            product = cursor.fetchone()
            if product is None:
                messagebox.showerror("Error", "Product not found.")
                return
            name, category_id, stock, price = product
            cursor.execute("SELECT name FROM categories WHERE id=%s", (category_id,))
            category_name = cursor.fetchone()[0] if category_id else "None"
        except mysql.connector.Error as e:
            self.status_var.set(f"Error fetching product: {str(e)}")
            return
        finally:
            cursor.close()
            conn.close()

        modify_win = tk.Toplevel(self.root)
        modify_win.title("Modify Product")
        modify_win.geometry("300x300")
        modify_win.grab_set()

        tk.Label(modify_win, text="Name").pack(pady=5)
        name_entry = tk.Entry(modify_win)
        name_entry.insert(0, name)
        name_entry.pack(pady=5)

        tk.Label(modify_win, text="Category").pack(pady=5)
        categories = self.get_category_dict()
        category_names = ["None"] + list(categories.keys())
        category_var = tk.StringVar(value=category_name)
        category_combo = ttk.Combobox(modify_win, textvariable=category_var, values=category_names, state="readonly")
        category_combo.pack(pady=5)

        tk.Label(modify_win, text="Stock").pack(pady=5)
        stock_entry = tk.Entry(modify_win)
        stock_entry.insert(0, str(stock))
        stock_entry.pack(pady=5)

        tk.Label(modify_win, text="Price").pack(pady=5)
        price_entry = tk.Entry(modify_win)
        price_entry.insert(0, str(price))
        price_entry.pack(pady=5)

        def update_product():
            new_name = name_entry.get().strip()
            new_category = category_var.get()
            new_stock = stock_entry.get().strip()
            new_price = price_entry.get().strip()

            if not all([new_name, new_stock, new_price]):
                messagebox.showerror("Error", "Name, stock, and price are required.")
                return

            try:
                new_stock = int(new_stock)
                new_price = float(new_price)
            except ValueError:
                messagebox.showerror("Error", "Stock must be an integer and price must be a number.")
                return

            new_category_id = None if new_category == "None" else categories.get(new_category)
            conn = connect_db()
            if conn is None:
                return
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE products SET name=%s, category_id=%s, stock=%s, price=%s WHERE id=%s",
                    (new_name, new_category_id, new_stock, new_price, product_id)
                )
                conn.commit()
                self.log_activity("Modify Product", f"Modified product: {new_name}")
                self.status_var.set("Product updated successfully.")
                if new_stock < 10:
                    self.add_notification(f"Low stock alert: {new_name} has only {new_stock} units.", "warning")
                elif new_stock > 100:
                    self.add_notification(f"High stock notice: {new_name} has {new_stock} units.", "info")
                modify_win.destroy()
                self.load_products()
                if "Dashboard" in [w.winfo_name() for w in self.main_frame.winfo_children()]:
                    self.load_recent_products()
            except mysql.connector.Error as e:
                self.status_var.set(f"Error updating product: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        tk.Button(modify_win, text="Update", command=update_product).pack(pady=10)

    def remove_product(self):
        product_id = self.get_selected_product()
        if product_id is None:
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this product?"):
            conn = connect_db()
            if conn is None:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM products WHERE id=%s", (product_id,))
                name = cursor.fetchone()[0]
                cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
                conn.commit()
                self.log_activity("Remove Product", f"Deleted product: {name}")
                self.status_var.set("Product deleted successfully.")
                self.load_products()
                if "Dashboard" in [w.winfo_name() for w in self.main_frame.winfo_children()]:
                    self.load_recent_products()
            except mysql.connector.Error as e:
                self.status_var.set(f"Error deleting product: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def get_selected_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a product.")
            return None
        values = self.tree.item(selected, 'values')
        return values[0]  # ID

    def on_double_click(self, event):
        self.open_modify_product_window()

    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        if col in ["ID", "Stock"]:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        elif col == "Price":
            l.sort(key=lambda t: float(t[0].replace("P", "")), reverse=reverse)
        else:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def add_notification(self, message, notification_type="info"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notifications.append((timestamp, notification_type, message))

    def show_notifications(self, event):
        if not self.notifications:
            messagebox.showinfo("Notifications", "No notifications.")
        else:
            notif_win = tk.Toplevel(self.root)
            notif_win.title("Notifications")
            notif_win.geometry("500x400")
            text_widget = tk.Text(notif_win, height=20, width=60, font=self.font)
            text_widget.pack(pady=10)
            for ts, ntype, msg in self.notifications:
                text_widget.insert(tk.END, f"{ts} [{ntype.upper()}]: {msg}\n")
            tk.Button(notif_win, text="Clear Notifications", command=lambda: [self.notifications.clear(), notif_win.destroy()],
                     bg=self.primary_color, fg=self.secondary_color, font=self.font).pack(pady=5)

    def get_category_dict(self):
        conn = connect_db()
        if conn is None:
            return {}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = {row[1]: row[0] for row in cursor.fetchall()}
            return categories
        except mysql.connector.Error as e:
            self.status_var.set(f"Error fetching categories: {str(e)}")
            return {}
        finally:
            cursor.close()
            conn.close()

    def load_categories(self):
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories")
            categories = ["All"] + [row[0] for row in cursor.fetchall()]
            self.category_filter_combo["values"] = categories
            self.category_filter_var.set("All")
        except mysql.connector.Error as e:
            self.status_var.set(f"Error loading categories: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def update_summary(self):
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(stock) FROM products")
            total_stock = cursor.fetchone()[0] or 0
            self.summary_label.config(text=f"Total Products: {total_products} | Total Stock: {total_stock}")
        except mysql.connector.Error as e:
            self.status_var.set(f"Error updating summary: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def configure_role_access(self):
        if self.user_role != "admin":
            self.btn_add.config(state=tk.DISABLED)
            self.btn_modify.config(state=tk.DISABLED)
            self.btn_remove.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root, user_role="admin", username="admin", user_id=1)
    root.mainloop()
