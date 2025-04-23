# Jollibee Inventory Management System

This is a comprehensive inventory management system designed for Jollibee, built with **Python**, **Tkinter** for the graphical user interface, and **MySQL** for data storage. The system includes **user authentication** with sign-up and login, **role-based access control** (admin and user roles), and a wide range of inventory management features. 

> **Note**: The project has been refactored from a single-file structure into a modular design with multiple files, now located in the `/sf/` folder, to improve organization and scalability.

## Features

- **User Authentication**:
  - Secure sign-up and login with password hashing (SHA-256).
  - Role-based access:
    - **Admin**: Full access to manage products, categories, users, and generate reports.
    - **User**: Limited access to view products and reports.

- **Inventory Management**:
  - Add, modify, and remove products with details like name, category, stock, and price.
  - Manage product categories (add, edit, delete).
  - Search and filter products by name, category, and price range.

- **Dashboard**:
  - Displays key metrics such as total products, categories, low stock items, and total users.
  - Shows a list of recently added products.

- **Reports**:
  - Generate reports including low stock, high stock, most expensive, least expensive products, and category summaries.
  - Export reports as text for further use.

- **Activity Log**:
  - Tracks user actions (e.g., adding products, modifying users) for auditing purposes.

- **Settings**:
  - Change password, backup and restore the database, and switch between light/dark themes.

- **Notifications**:
  - Alerts for low stock (<10 units) and high stock (>100 units) levels.

## Requirements

- **Python 3.7+** (Tested up to Python 3.12)
- **Tkinter** (typically included with Python)
- **MySQL Server** (e.g., MySQL 8+)
- **mysql-connector-python** library

## Installation

1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/golgrax/jollibee-inventory.git
   cd jollibee-inventory
   ```

2. **Create and Activate a Virtual Environment** (recommended):
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade mysql-connector-python
   ```

## MySQL Setup

1. **Install MySQL Server** (if not already installed):
   ```bash
   sudo apt-get update
   sudo apt-get install mysql-server
   ```

2. **Create Database and User**:
   - Log in to MySQL as root:
     ```bash
     sudo mysql
     ```
   - Create the database:
     ```sql
     CREATE DATABASE jollibee_inventory;
     ```
   - Create a user and grant privileges:
     ```sql
     CREATE USER 'test'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Test1234!';
     GRANT ALL PRIVILEGES ON jollibee_inventory.* TO 'test'@'localhost';
     FLUSH PRIVILEGES;
     ```

3. **Verify Configuration**:
   - The default database configuration is in `sf/database.py`:
     ```python
     DB_CONFIG = {
         'user': 'test',
         'password': 'Test1234!',
         'host': 'localhost',
         'database': 'jollibee_inventory',
         'ssl_disabled': True
     }
     ```
   - Update these values if your MySQL setup differs.

## Usage

1. **Run the Application**:
   - Ensure you are in the project directory and the virtual environment is activated.
   - Execute:
     ```bash
     python sf/main.py
     ```

2. **Login or Sign Up**:
   - **Sign Up**: Create a new account by providing a username, password, and role (admin or user).
   - **Login**: Use existing credentials to access the system.

3. **Inventory Management**:
   - **Dashboard**: View key metrics (total products, categories, low stock, users) and recent products.
   - **Products**: Add, modify, or remove products; search by name, category, or price range (admin-only for modifications).
   - **Categories**: Add, edit, or delete product categories (admin-only).
   - **Users**: Manage user accounts (add, edit, delete; admin-only).
   - **Reports**: Generate and export reports (e.g., low stock, high stock).
   - **Activity Log**: Review user actions with timestamps.
   - **Settings**: Change password, backup/restore database, or switch themes.

## File Structure

The project is now organized into multiple files within the `/sf/` folder for modularity:

- **`sf/main.py`**:
  - Entry point of the application. Initializes the database and launches the login window.
- **`sf/login.py`**:
  - Manages the login interface and redirects to signup if needed.
- **`sf/signup.py`**:
  - Handles user registration with role selection.
- **`sf/inventory.py`**:
  - Core inventory management interface, including dashboard, products, categories, users, reports, activity log, and settings.
- **`sf/user_management.py`**:
  - Provides admin functionality to add, edit, and delete users.
- **`sf/database.py`**:
  - Contains database connection logic and table initialization functions.

## Troubleshooting

- **SSL Errors**:
  - If you encounter SSL-related issues (e.g., `AttributeError: module 'ssl' has no attribute 'wrap_socket'`), ensure your MySQL user uses `mysql_native_password` and that `'ssl_disabled': True` is set in `DB_CONFIG`.
- **Invalid Credentials**:
  - Verify that the username and password in `sf/database.py` match your MySQL setup.
- **PEP 668 Issues**:
  - On Debian/Ubuntu systems, use a virtual environment to install dependencies due to system-wide Python restrictions.
- **Database Connection Failed**:
  - Ensure MySQL Server is running (`sudo systemctl start mysql`) and the database/user exist.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for enhancements or bug fixes.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

This updated `README.md` reflects the transition from a single-file application to a modular structure in the `/sf/` folder, providing detailed instructions and an overview of the system's enhanced capabilities. Let me know if you need further refinements!
