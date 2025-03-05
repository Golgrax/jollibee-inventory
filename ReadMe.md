# Jollibee Inventory Management

This is a simple inventory management system built with **Python**, **Tkinter** (for the GUI), and **MySQL** for data storage. It supports **user authentication** (with sign-up and login), **role-based access** (admin or user), and basic inventory operations (add, modify, remove, search).

## Features

1. **User Authentication**  
   - Users can **sign up** and **log in**.  
   - Passwords are securely hashed (SHA-256).  
   - Roles:
     - **admin**: can add, modify, and remove products.
     - **user**: can only view products.

2. **Product Management**  
   - **Add Product**: Enter product name, stock, and price.  
   - **Modify Product**: Update name, stock, and price.  
   - **Remove Product**: Delete a product permanently.

3. **Search Function**  
   - Search for products by name in real time.

4. **Summary Statistics**  
   - Displays total number of products, total stock, and total inventory value.

5. **Clean Window Flow**  
   - When the user signs up or logs in successfully, the previous window is closed to avoid confusion.

## Requirements

- **Python 3.7+** (Tested up to Python 3.12)
- **Tkinter** (usually comes pre-installed with Python on most systems)
- **MySQL Server** (e.g., MySQL 8+)
- **mysql-connector-python** library

## MySQL Setup

1. **Install MySQL Server** (if not already installed)  
   ```bash
   sudo apt-get update
   sudo apt-get install mysql-server
   ```
2. **Create a Database and User**  
   - Log in to MySQL as root or a privileged user:
     ```bash
     sudo mysql
     ```
   - Create the `jollibee_inventory` database (if you haven’t already):
     ```sql
     CREATE DATABASE jollibee_inventory;
     ```
   - Create a user (e.g., `test`) with a secure password:
     ```sql
     CREATE USER 'test'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Test1234!';
     GRANT ALL PRIVILEGES ON jollibee_inventory.* TO 'test'@'localhost';
     FLUSH PRIVILEGES;
     ```
3. **Adjust MySQL Authentication (If Needed)**  
   - Some MySQL configurations default to the `caching_sha2_password` plugin, which requires SSL. If you encounter SSL errors, ensure your user is set to `mysql_native_password`, as shown above.

## Installation

1. **Clone or Download** this repository into a local folder:
   ```bash
   git clone https://github.com/golgrax/jollibee-inventory.git
   cd jollibee-inventory
   ```
   (Or simply download the code files into a directory of your choice.)

2. **Create and Activate a Virtual Environment** (recommended):
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install --upgrade mysql-connector-python
   ```
   If you’re on a Debian/Ubuntu system with PEP 668 restrictions, make sure you’re inside the virtual environment to install the library.

## Usage

1. **Edit `DB_CONFIG` (If Necessary)**  
   In `main.py` (or whichever file contains your code), ensure the following matches your MySQL setup:
   ```python
   DB_CONFIG = {
       'user': 'test',
       'password': 'Test1234!',
       'host': 'localhost',
       'database': 'jollibee_inventory',
       'ssl_disabled': True
   }
   ```
2. **Initialize the Database and Run the App**  
   - The code will create (if not existing) and set up the tables when you run the script.
   - Simply run:
     ```bash
     python main.py
     ```
   - This will open the **Login Window**.

3. **Login or Sign Up**  
   - **Sign Up**: Enter a new username, password, confirm password, and choose a role (admin or user).  
   - **Login**: Enter existing credentials.

4. **Inventory Window**  
   - Once logged in, you’ll see the main inventory interface:
     - **Search**: Enter a product name (partial or full) to filter.  
     - **Add**: (Admins only) Adds a new product.  
     - **Modify**: (Admins only) Updates selected product info.  
     - **Remove**: (Admins only) Deletes the selected product.  
     - **Refresh**: Reloads the product list from the database.
   - **Summary**: Shows total product count, total stock, and total inventory value at the bottom.

## Troubleshooting

- **SSL Errors**: If you see `AttributeError: module 'ssl' has no attribute 'wrap_socket'`, either disable SSL (`'ssl_disabled': True`) or use a compatible version of mysql-connector-python in a virtual environment.
- **Invalid Credentials**: Double-check that you created your user in MySQL with the correct password and plugin (`mysql_native_password`).
- **PEP 668 / System-Wide Install Issues**: On Debian/Ubuntu-based systems, use a virtual environment or install via apt if you prefer system-wide packages.

## Contributing

Feel free to fork this project and submit pull requests for any improvements or bug fixes.

## License

[MIT License](https://opensource.org/licenses/MIT).

