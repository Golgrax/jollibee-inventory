from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'BSIT2-2GROUP10' # CAUTION!!! I changed the default, what if we used ENV instead para maging more secured.

DB_CONFIG = {
    'user': 'test',
    'password': 'Test1234!',
    'host': 'localhost',
    'database': 'jollibee_inventory',
    'ssl_disabled': True
}



@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))



def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Access denied. Admins only.", "error")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action, details):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
            (user_id, action, details)
        )
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error logging activity: {e}")
    finally:
        cursor.close()
        conn.close()

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_db()
        if conn is None:
            flash("Database connection failed.", "error")
            return render_template('login.html')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            log_activity(user[0], "Login", f"User {username} logged in")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        role = request.form['role']
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template('signup.html')
        hashed = generate_password_hash(password)
        conn = connect_db()
        if conn is None:
            flash("Database connection failed.", "error")
            return render_template('signup.html')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed, role)
            )
            conn.commit()
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['username'] = username
            session['role'] = role
            log_activity(user_id, "Signup", f"User {username} signed up with role {role}")
            return redirect(url_for('dashboard'))
        except mysql.connector.IntegrityError:
            flash("Username already exists.", "error")
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    log_activity(session['user_id'], "Logout", f"User {session['username']} logged out")
    session.clear()
    return redirect(url_for('login'))

# Main Routes
@app.route('/dashboard')
@login_required
def dashboard():
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('dashboard.html')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM categories")
    total_categories = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock < 10")
    low_stock = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("""
        SELECT p.id, p.name, c.name, p.stock, p.price
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
        LIMIT 5
    """)
    recent_products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard.html',
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        total_users=total_users,
        recent_products=recent_products)

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('products.html', products=[], categories=[])
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    category = request.args.get('category', 'All')
    search_term = request.args.get('search', '')
    min_price = request.args.get('min_price', '0')
    max_price = request.args.get('max_price', '0')
    try:
        min_price = float(min_price)
        max_price = float(max_price)
    except ValueError:
        min_price = 0
        max_price = 0

    query = """
        SELECT p.id, p.name, c.name, p.stock, p.price
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.name LIKE %s AND p.price BETWEEN %s AND %s
    """
    params = [f"%{search_term}%", min_price, max_price]
    if category != 'All' and category.isdigit(): # Ensure category is a digit if not 'All'
        query += " AND c.id = %s"
        params.append(int(category))
    elif category != 'All': # Handle potential non-digit category selection gracefully
        flash("Invalid category filter selected.", "warning")


    cursor.execute(query, params)
    products_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('products.html',
        products=products_data,
        categories=categories,
        selected_category=category,
        search_term=search_term,
        min_price=min_price,
        max_price=max_price,
        is_admin=session.get('role') == 'admin')

@app.route('/products/add', methods=['GET', 'POST'])
@admin_required # Using admin_required decorator
def add_product():
    # No need for manual role check:
    # if session.get('role') != 'admin':
    #     flash("Access denied. Admins only.", "error")
    #     return redirect(url_for('products'))
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('add_product.html', categories=[])
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category'] if request.form['category'] != 'None' else None
        stock = request.form['stock']
        price = request.form['price']
        try:
            stock = int(stock)
            price = float(price)
        except ValueError:
            flash("Invalid stock or price.", "error")
            cursor.close()
            conn.close()
            return render_template('add_product.html', categories=categories)
        try:
            cursor.execute(
                "INSERT INTO products (name, category_id, stock, price) VALUES (%s, %s, %s, %s)",
                (name, category_id, stock, price)
            )
            conn.commit()
            log_activity(session['user_id'], "Add Product", f"Added product: {name}")
            flash("Product added successfully!", "success")
            return redirect(url_for('products'))
        except mysql.connector.Error as e:
            flash(f"Error adding product: {e}", "error")
        finally:
            cursor.close()
            conn.close()
    else: # GET request
        cursor.close()
        conn.close()
    return render_template('add_product.html', categories=categories)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required # Using admin_required decorator
def edit_product(id):
    # No need for manual role check
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('edit_product.html', product=None, categories=[])
    cursor = conn.cursor(dictionary=True) # Use dictionary cursor for easier access

    if request.method == 'POST':
        name = request.form['name']
        category_id = request.form['category'] if request.form['category'] != 'None' else None
        stock = request.form['stock']
        price = request.form['price']
        try:
            stock = int(stock)
            price = float(price)
        except ValueError:
            flash("Invalid stock or price.", "error")
            # Refetch product and categories for rendering the form again
            cursor.execute("SELECT id, name, category_id, stock, price FROM products WHERE id=%s", (id,))
            product = cursor.fetchone()
            cursor.execute("SELECT id, name FROM categories")
            categories_list = cursor.fetchall() # Fetch as list of dicts
            cursor.close()
            conn.close()
            return render_template('edit_product.html', product=product, categories=categories_list)
        try:
            cursor.execute(
                "UPDATE products SET name=%s, category_id=%s, stock=%s, price=%s WHERE id=%s",
                (name, category_id, stock, price, id)
            )
            conn.commit()
            log_activity(session['user_id'], "Edit Product", f"Edited product ID: {id}, Name: {name}")
            flash("Product updated successfully!", "success")
            return redirect(url_for('products'))
        except mysql.connector.Error as e:
            flash(f"Error updating product: {e}", "error")
        finally:
            # cursor.close() # cursor might be closed if ValueError happened
            # conn.close() # conn might be closed if ValueError happened
            # Ensure closure if not already closed
            if cursor and not cursor.is_closed():
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
    else: # GET request
        cursor.execute("SELECT id, name, category_id, stock, price FROM products WHERE id=%s", (id,))
        product = cursor.fetchone()
        cursor.execute("SELECT id, name FROM categories")
        categories_list = cursor.fetchall() # Fetch as list of dicts
        cursor.close()
        conn.close()
        if not product:
            flash("Product not found.", "error")
            return redirect(url_for('products'))
        return render_template('edit_product.html', product=product, categories=categories_list)


@app.route('/products/delete/<int:id>')
@admin_required # Using admin_required decorator
def delete_product(id):
    # No need for manual role check
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('products'))
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM products WHERE id=%s", (id,))
        product_record = cursor.fetchone()
        if not product_record:
            flash("Product not found for deletion.", "error")
            return redirect(url_for('products'))
        name = product_record[0]

        cursor.execute("DELETE FROM products WHERE id=%s", (id,))
        conn.commit()
        log_activity(session['user_id'], "Delete Product", f"Deleted product: {name} (ID: {id})")
        flash("Product deleted successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Error deleting product: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('products'))

@app.route('/categories')
@login_required
def categories():
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('categories.html', categories=[])
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('categories.html', categories=categories, is_admin=session.get('role') == 'admin')

@app.route('/categories/add', methods=['GET', 'POST'])
@admin_required # Changed from @login_required and manual check for consistency
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        conn = connect_db()
        if conn is None:
            flash("Database connection failed.", "error")
            return render_template('add_category.html')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
            conn.commit()
            log_activity(session['user_id'], "Add Category", f"Added category: {name}")
            flash("Category added successfully!", "success")
            return redirect(url_for('categories'))
        except mysql.connector.IntegrityError:
            flash("Category name already exists.", "error")
        except mysql.connector.Error as e:
            flash(f"Error adding category: {e}", "error")
        finally:
            cursor.close()
            conn.close()
    return render_template('add_category.html')


@app.route('/categories/delete/<int:id>')
@admin_required
def delete_category(id):
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('categories'))

    cursor = conn.cursor()
    try:
        # Get category name for logging and messages
        cursor.execute("SELECT name FROM categories WHERE id = %s", (id,))
        category_record = cursor.fetchone()

        if not category_record:
            flash("Category not found.", "error")
            return redirect(url_for('categories'))

        category_name = category_record[0]

        # Step 1: Update products associated with this category to set category_id to NULL
        # This makes product uncategorized instead of deleting them or causing FK error.
        # Assumes 'products' table has 'category_id' column that allows NULL.
        cursor.execute("UPDATE products SET category_id = NULL WHERE category_id = %s", (id,))

        # Step 2: Delete the category
        cursor.execute("DELETE FROM categories WHERE id = %s", (id,))

        conn.commit() # Commit both operations

        log_activity(session['user_id'], "Delete Category", f"Deleted category: {category_name} (ID: {id})")
        flash(f"Category '{category_name}' deleted successfully. Associated products are now uncategorized.", "success")

    except mysql.connector.Error as e:
        if conn.is_connected(): # Check if connection is still alive before rollback
            conn.rollback()
        flash(f"Error deleting category: {e}", "error")
        print(f"Database error during category deletion: {e}") # For server-side logs
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('categories'))

@app.route('/users')
@admin_required
def users():
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('users.html', users=[])
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users_data)

@app.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed = generate_password_hash(password)
        conn = connect_db()
        if conn is None:
            flash("Database connection failed.", "error")
            return render_template('add_user.html')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, hashed, role)
            )
            conn.commit()
            log_activity(session['user_id'], "Add User", f"Added user: {username}")
            flash("User added successfully!", "success")
            return redirect(url_for('users'))
        except mysql.connector.IntegrityError:
            flash("Username already exists.", "error")
        except mysql.connector.Error as e:
            flash(f"Error adding user: {e}", "error")
        finally:
            cursor.close()
            conn.close()
    return render_template('add_user.html')

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('edit_user.html', user=None)

    # Use dictionary=True for easier access in template if needed, though user is tuple here
    cursor = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # Optional: only update if provided
        role = request.form['role']

        try:
            if password:
                hashed = generate_password_hash(password)
                cursor.execute(
                    "UPDATE users SET username=%s, password=%s, role=%s WHERE id=%s",
                    (username, hashed, role, id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username=%s, role=%s WHERE id=%s",
                    (username, role, id)
                )
            conn.commit()
            log_activity(session['user_id'], "Edit User", f"Edited user ID: {id}, Username: {username}")
            flash("User updated successfully!", "success")
            return redirect(url_for('users'))
        except mysql.connector.Error as e:
            flash(f"Error updating user: {e}", "error")
            # If error, need to refetch user data for the form
            cursor.execute("SELECT id, username, role FROM users WHERE id=%s", (id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template('edit_user.html', user=user_data)
        finally:
            if cursor and not cursor.is_closed():
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
    else: # GET request
        cursor.execute("SELECT id, username, role FROM users WHERE id=%s", (id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if not user_data:
            flash("User not found.", "error")
            return redirect(url_for('users'))
        return render_template('edit_user.html', user=user_data)


@app.route('/users/delete/<int:id>')
@admin_required
def delete_user(id):
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('users'))
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users WHERE id=%s", (id,))
        user_record = cursor.fetchone()
        if not user_record:
            flash("User not found for deletion.", "error")
            return redirect(url_for('users'))

        username = user_record[0]
        if username == session['username']:
            flash("Cannot delete yourself.", "error")
            return redirect(url_for('users'))

        cursor.execute("DELETE FROM users WHERE id=%s", (id,))
        conn.commit()
        log_activity(session['user_id'], "Delete User", f"Deleted user: {username} (ID: {id})")
        flash("User deleted successfully!", "success")
    except mysql.connector.Error as e:
        flash(f"Error deleting user: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('users'))

@app.route('/activity_log')
@login_required
def activity_log():
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return render_template('activity_log.html', logs=[])
    cursor = conn.cursor()
    # Consider adding pagination for large logs
    cursor.execute("""
        SELECT al.timestamp, u.username, al.action, al.details
        FROM activity_log al
        JOIN users u ON al.user_id = u.id
        ORDER BY al.timestamp DESC
        LIMIT 100
    """) # Added LIMIT for performance
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('activity_log.html', logs=logs)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        old_pass = request.form['old_password']
        new_pass = request.form['new_password']
        confirm_pass = request.form['confirm_password']

        if not old_pass or not new_pass or not confirm_pass:
            flash("All password fields are required.", "error")
            return render_template('settings.html')

        if new_pass != confirm_pass:
            flash("New passwords do not match.", "error")
            return render_template('settings.html')

        conn = connect_db()
        if conn is None:
            flash("Database connection failed.", "error")
            return render_template('settings.html')

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password FROM users WHERE id=%s", (session['user_id'],))
            current_hash_record = cursor.fetchone()
            if not current_hash_record:
                flash("User not found.", "error") # Should not happen if logged in
                return redirect(url_for('login'))

            current_hash = current_hash_record[0]
            if not check_password_hash(current_hash, old_pass):
                flash("Old password is incorrect.", "error")
                cursor.close()
                conn.close()
                return render_template('settings.html')

            new_hash = generate_password_hash(new_pass)
            cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_hash, session['user_id']))
            conn.commit()
            log_activity(session['user_id'], "Change Password", "User changed their password")
            flash("Password changed successfully!", "success")
        except mysql.connector.Error as e:
            flash(f"Error changing password: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('settings')) # Redirect to clear form or show success

    return render_template('settings.html')

@app.route('/backup')
@admin_required # Changed to admin_required as this is a sensitive operation
def backup():
    conn = connect_db()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect(url_for('settings')) # Or dashboard

    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        backup_data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}") # Use f-string carefully, table names from SHOW TABLES are safe

            # Fetch column names for context if needed, though json.dump handles tuples fine
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            # Store data as list of dictionaries for better readability in JSON
            backup_data[table] = [dict(zip(column_names, row)) for row in rows]

        backup_filename = "inventory_backup.json"
        with open(backup_filename, "w") as f:
            json.dump(backup_data, f, indent=4, default=str) # default=str for datetime etc.

        log_activity(session['user_id'], "Database Backup", f"Database backed up to {backup_filename}")
        flash(f"Database backed up to '{backup_filename}'.", "success")
    except mysql.connector.Error as e:
        flash(f"Error during backup: {e}", "error")
    except IOError as e:
        flash(f"Error writing backup file: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('settings')) # Or dashboard


# app name
@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
# defining function
  return render_template("404.html"), 404


if __name__ == '__main__':
    app.run(debug=True)
