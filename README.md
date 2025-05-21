# Jollibee Inventory Management System (Flask Web Application)

This is a web-based inventory management system designed for Jollibee, built with **Python**, **Flask** for the web framework, and **MySQL** for data storage. The system includes **user authentication** with sign-up and login, **role-based access control** (admin and user roles), and a range of inventory management features.

## Features

- **User Authentication**:
  - Secure sign-up and login with password hashing (`werkzeug.security`).
  - Role-based access:
    - **Admin**: Full access to manage products, categories, users, view activity logs, and perform backups.
    - **User**: Access to view products, dashboard, and manage their own settings (e.g., change password).

- **Inventory Management**:
  - Add, modify, and remove products with details like name, category, stock, and price.
  - Manage product categories (add, edit, delete).
  - Search and filter products by name, category, and price range.

- **Dashboard**:
  - Displays key metrics such as total products, categories, low stock items, and total users.
  - Shows a list of recently added products.

- **Activity Log**:
  - Tracks user actions (e.g., login, signup, adding products, modifying users) for auditing purposes.

- **Settings**:
  - Users can change their password.
  - Admins can initiate a database backup (to a JSON file).

## Prerequisites

- **Python 3.7+**
- **Git** (for cloning the repository)
- **MySQL Server** (Version 8.0+ recommended for compatibility with default authentication plugins; 5.7+ may also work but might require `mysql_native_password`)
- **MySQL Workbench** (Recommended for easier database management, but optional)
- A Web Browser

## Setup Instructions

Follow these steps to set up and run the application:

### 1. MySQL Database and User Setup

Your Flask application needs a dedicated MySQL database and user. You can set this up using the MySQL command line or MySQL Workbench.

**Your application expects the following database configuration (defined in `app.py`):**
-   **User:** `test`
-   **Password:** `Test1234!`
-   **Host:** `localhost`
-   **Database Name:** `jollibee_inventory`

**Method A: Using MySQL Command Line**

   a.  **Install MySQL Server:**
        *   **Linux (Debian/Ubuntu):**
  ```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
  ```    
You might need to run `sudo mysql_secure_installation` for initial setup.
        *   **Windows:** Download the MySQL Installer from the [official MySQL website](https://dev.mysql.com/downloads/installer/) and follow the installation instructions. Ensure the MySQL Server is added to your system's PATH or use the MySQL Command Line Client installed with it.
        *   **macOS:** You can use Homebrew: `brew install mysql` and `brew services start mysql`.

   b.  **Connect to MySQL as an administrative user (e.g., root):**
        *   **Linux/macOS:**
  ```bash
  sudo mysql
  # Or if you have a root password set:
  # mysql -u root -p
  ```
  *   **Windows:** Open the MySQL Command Line Client or PowerShell/CMD and type:
```bash
mysql -u root -p
```
  (Enter your MySQL root password when prompted).

   c.  **Execute the following SQL commands:**
   
        
        -- Create the dedicated user for your application.
        -- For modern MySQL versions (8.0+), the server's default authentication plugin 
        -- (often 'caching_sha2_password') is preferred and typically doesn't require 
        -- specifying 'IDENTIFIED WITH mysql_native_password'.
        -- If you encounter "Plugin 'mysql_native_password' is not loaded", using the command below is correct.
        CREATE USER IF NOT EXISTS 'test'@'localhost' IDENTIFIED BY 'Test1234!';

        -- Create the database for your application.
        CREATE DATABASE IF NOT EXISTS jollibee_inventory;

        -- Grant all necessary privileges to your application user on the new database.
        GRANT ALL PRIVILEGES ON jollibee_inventory.* TO 'test'@'localhost';

        -- Apply the privilege changes.
        FLUSH PRIVILEGES;

        -- Exit MySQL
        EXIT;
        

**Method B: Using MySQL Workbench (Recommended for Visual Setup - All OS)**

   a.  **Install MySQL Workbench:** Download from the [official MySQL website](https://dev.mysql.com/downloads/workbench/) and install it.

   b.  **Connect to your MySQL Server as an administrative user (e.g., `root`):**
        1.  Open MySQL Workbench.
        2.  Click the `+` next to "MySQL Connections".
        3.  Configure the connection:
            *   **Connection Name:** `localhost_admin` (or similar)
            *   **Hostname:** `127.0.0.1` or `localhost`
            *   **Username:** `root`
            *   **Password:** Store your MySQL root password in the vault.
        4.  Test and save the connection. Double-click to open it.

   c.  **Open a new SQL Query Tab and execute the following SQL commands:**
        
        -- Create the dedicated user for your application.
        -- For modern MySQL versions (8.0+), the server's default authentication plugin 
        -- (often 'caching_sha2_password') is preferred.
        CREATE USER IF NOT EXISTS 'test'@'localhost' IDENTIFIED BY 'Test1234!';

        -- Create the database for your application.
        CREATE DATABASE IF NOT EXISTS jollibee_inventory;

        -- Grant all necessary privileges to your application user on the new database.
        GRANT ALL PRIVILEGES ON jollibee_inventory.* TO 'test'@'localhost';

        -- Apply the privilege changes.
        FLUSH PRIVILEGES;
        

### 2. Create Database Tables

Once the database (`jollibee_inventory`) and user (`test`) are created, you need to create the necessary tables.

   a.  **Connect to the `jollibee_inventory` database:**
        *   **MySQL Command Line:**
            ```bash
            mysql -u test -p jollibee_inventory
            ```
            (Enter password `Test1234!`)
        *   **MySQL Workbench:**
            1.  You can create a new connection for the `test` user (similar to how you created the `root` connection, but use `test` as username and `jollibee_inventory` as the "Default Schema").
            2.  Or, in your `root` connection, double-click `jollibee_inventory` in the "SCHEMAS" panel to make it the default, or type `USE jollibee_inventory;` in an SQL tab.

   b.  **Execute the following SQL `CREATE TABLE` statements:**
        
        USE jollibee_inventory;

        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category_id INT,
            stock INT NOT NULL DEFAULT 0,
            price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(255) NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        
In MySQL Workbench, you can check the "SCHEMAS" panel. Right-click `jollibee_inventory` and "Refresh All" to see the created tables.

### 3. Application Setup

   a.  **Clone or Download the Repository:**
        If you have `git` installed:
  ```bash
git clone https://github.com/Golgrax/jollibee-inventory.git
cd jollibee-inventory
  ```
Otherwise, download the ZIP from `https://github.com/Golgrax/jollibee-inventory/archive/refs/heads/main.zip` (or your desired branch) and extract it. Navigate into the project folder (e.g., `jollibee-inventory` or `jollibee-inventory-main`).

   b.  **Create and Activate a Virtual Environment** (highly recommended):
        Open your terminal or command prompt in the project directory.
  ```bash
  python3 -m venv venv
  # Or on Windows:
  # python -m venv venv
  ```
  Activate the virtual environment:
  *   **Linux/macOS:**
  ```bash
  source venv/bin/activate
  ```
  *   **Windows (CMD):**
  ```bash
    venv\Scripts\activate.bat
  ```
  *   **Windows (PowerShell):**
  ```bash
  venv\Scripts\Activate.ps1
  ```
  (If you get an error on PowerShell, you might need to run: `Set-ExecutionPolicy Unrestricted -Scope Process` first, then try activating again.)

   c.  **Install Python Dependencies:**
        Ensure you have a file named `requirements.txt` in your project's root directory with the following content:
  ```txt
  Flask
  mysql-connector-python
  Werkzeug
  ```
  Then, install the dependencies (make sure your virtual environment is activated):
  ```bash
  pip install -r requirements.txt
  ```

### 4. Verify Database Configuration in `app.py`

Open the `app.py` file and ensure the `DB_CONFIG` dictionary matches your MySQL setup (it should by default if you followed the steps above):
```python
DB_CONFIG = {
    'user': 'test',
    'password': 'Test1234!',
    'host': 'localhost',
    'database': 'jollibee_inventory',
    'ssl_disabled': True
}
```
The `ssl_disabled: True` is important if you haven't configured SSL for your MySQL server, which is common for local development.

## Running the Application

1.  Ensure your MySQL server is running.
2.  Ensure your virtual environment is activated (you should see `(venv)` in your terminal prompt).
3.  Navigate to the project directory in your terminal.
4.  Run the Flask application:
    ```bash
    python app.py
    # Or python3 app.py if 'python' on your system defaults to Python 2
    ```
5.  Open your web browser and go to `http://127.0.0.1:5000/`.

## Usage

1.  **Sign Up**: The first time you access the application, you'll likely need to sign up for an account. You can create an 'admin' or 'user' role.
    *   For an initial admin account, use "admin" as the role during signup.
2.  **Login**: Use your registered credentials to log in.
3.  **Navigate**:
    *   **Dashboard**: View key metrics and recent products.
    *   **Products**: View, add, edit, or delete products (admins have full CRUD, users typically have read-only).
    *   **Categories**: Manage product categories (admin-only).
    *   **Users**: Manage user accounts (admin-only).
    *   **Activity Log**: Review user actions.
    *   **Settings**: Change your password. Admins can also backup the database.

## Troubleshooting

-   **Database Connection Failed / Access Denied / Authentication Plugin Issues:**
    *   Ensure MySQL Server is running (`sudo systemctl status mysql` on Linux, check Services on Windows).
    *   Verify the `user`, `password`, `host`, and `database` in `DB_CONFIG` in `app.py` exactly match the user and database you created in MySQL.
    *   Ensure the user `test` has privileges on the `jollibee_inventory` database (`GRANT ALL PRIVILEGES ON jollibee_inventory.* TO 'test'@'localhost';` followed by `FLUSH PRIVILEGES;`).
    *   **Authentication Plugin:**
        *   Modern MySQL versions (8.0+) often default to the `caching_sha2_password` authentication plugin. Older versions might have used `mysql_native_password`.
        *   If you encounter errors like `Plugin 'mysql_native_password' is not loaded` when trying to create the user with `IDENTIFIED WITH mysql_native_password BY ...`, simply use `IDENTIFIED BY ...` (as shown in the updated setup steps). This lets MySQL use its default plugin.
        *   The `mysql-connector-python` library used by this Flask application generally supports `caching_sha2_password` without any special configuration in `DB_CONFIG`.
        *   If you *must* use `mysql_native_password` (e.g., for compatibility with very old tools) and it's not enabled, you would need to configure your MySQL server to load it. This usually involves editing the MySQL configuration file (e.g., `my.cnf` or `mysqld.cnf`) to add `default_authentication_plugin=mysql_native_password` under the `[mysqld]` section and restarting the MySQL server. However, for this project, using the server's default is recommended.
-   **`No module named 'flask'` (or other modules):**
    *   Make sure your virtual environment is activated. You should see `(venv)` at the beginning of your terminal prompt.
    *   Ensure you've run `pip install -r requirements.txt` *within* the activated virtual environment.
-   **SSL Errors (e.g., `SSL connection error: SSL is required but the server doesn't support it`):**
    *   Ensure `'ssl_disabled': True` is in your `DB_CONFIG` in `app.py` if you are not using SSL with MySQL for local development.
    *   Alternatively, configure SSL on your MySQL server and adjust client connection parameters (more advanced).

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for enhancements or bug fixes.

## License

This project is licensed under the MIT License.

You can find the full text of the license here:
[https://github.com/Golgrax/jollibee-inventory/blob/main/LICENSE](https://github.com/Golgrax/jollibee-inventory/blob/main/LICENSE)
