from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))
CORS(app)  # Enable CORS for all routes

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'userdb'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'ssl_disabled': True
}

def get_db_connection():
    """Establish a connection to the MySQL database, with SQLite fallback"""
    try:
        # Extract config values individually with robust defaults
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'userdb')
        
        # Robust port parsing
        port_str = os.getenv('DB_PORT')
        port = int(port_str) if port_str and port_str.strip() else 3306
        
        print(f"Attempting MySQL connection to: {host}:{port}, user: {user}, db: {database}")
        
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            ssl_disabled=True,
            connect_timeout=5 # Add timeout for MySQL
        )
        print("MySQL connection successful!")
        return connection
    except Exception as err:
        print(f"MySQL connection failed: {err}")
        print("Falling back to SQLite...")
        # Fallback to SQLite
        try:
            # Use an absolute path for the SQLite database to ensure it's found
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users_local.db')
            print(f"Connecting to SQLite at: {db_path}")
            
            conn = sqlite3.connect(db_path, timeout=20.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create users table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            conn.commit()
            print("SQLite connection successful!")
            return conn
        except Exception as e:
            print(f"SQLite connection failed: {e}")
            return None

def initialize_database():
    """Initialize the database and create users table if it doesn't exist"""
    # Robust port parsing
    port_str = os.getenv('DB_PORT')
    port = int(port_str) if port_str and port_str.strip() else 3306
    
    # Try MySQL first
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            port=port,
            ssl_disabled=True,
            connect_timeout=5
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        db_name = os.getenv('DB_NAME', 'userdb')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
        
        # Now connect to the specific database
        connection.database = db_name
        
        # Check if phone column exists, if not, add it
        check_column_query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'phone'
        """
        cursor.execute(check_column_query, (db_name,))
        column_exists = cursor.fetchone()
        
        # Create users table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            phone VARCHAR(20),
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        
        # If phone column didn't exist, add it
        if not column_exists:
            alter_table_query = "ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email"
            cursor.execute(alter_table_query)
            connection.commit()
            print("Added phone column to users table")
        
        print("MySQL Database initialized successfully")
        cursor.close()
        connection.close()
        
    except Exception as err:
        print(f"MySQL initialization failed: {err}")
        # MySQL failed, try SQLite
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users_local.db')
            print(f"Initializing SQLite at: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create users table if it doesn't exist in SQLite
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            conn.commit()
            
            print("SQLite Database initialized successfully")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error initializing SQLite database: {e}")

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')

        # Validate input
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert user into database
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please check your network connection and database settings.'}), 500

        try:
            # Check if this is a SQLite connection
            is_sqlite = isinstance(connection, sqlite3.Connection)
            
            cursor = connection.cursor()
            if is_sqlite:
                insert_query = "INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)"
                cursor.execute(insert_query, (username, email, phone, hashed_password))
            else:
                insert_query = "INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (username, email, phone, hashed_password))
            connection.commit()
            cursor.close()
            return jsonify({'message': 'Registration successful'}), 201
        finally:
            connection.close()

    except (mysql.connector.IntegrityError, sqlite3.IntegrityError) as err:
        # Handle duplicate entry errors for both MySQL and SQLite
        error_str = str(err)
        if "Duplicate entry" in error_str or "UNIQUE constraint failed" in error_str:
            return jsonify({'error': 'Username or email already exists'}), 400
        else:
            return jsonify({'error': f'Database error: {error_str}'}), 500
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validate input
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        # Query user from database
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please check your network connection and database settings.'}), 500

        try:
            # Check if this is a SQLite connection
            is_sqlite = isinstance(connection, sqlite3.Connection)
            
            if is_sqlite:
                cursor = connection.cursor()
            else:
                cursor = connection.cursor(dictionary=True)
            
            if is_sqlite:
                select_query = "SELECT * FROM users WHERE username = ?"
                cursor.execute(select_query, (username,))
            else:
                select_query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(select_query, (username,))
            
            user = cursor.fetchone()
            cursor.close()

            # Check if user exists and password is correct
            if user and check_password_hash(user['password'], password):
                return jsonify({
                    'message': 'Login successful',
                    'username': username
                }), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        finally:
            connection.close()

    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/users', methods=['POST'])
def get_users():
    """Get all registered users"""
    try:
        data = request.get_json() or {}
        admin_password = data.get('adminPassword')

        # Verify admin password matches database password from environment
        if not admin_password or admin_password != os.getenv('DB_PASSWORD'):
            return jsonify({'error': 'Unauthorized: Incorrect admin password'}), 401

        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please check your network connection and database settings.'}), 500

        try:
            # Check if this is a SQLite connection
            is_sqlite = isinstance(connection, sqlite3.Connection)
            
            if is_sqlite:
                cursor = connection.cursor()
                # For SQLite, use datetime function to format the date
                cursor.execute("SELECT id, username, email, phone, password, datetime(created_at) as created_at FROM users")
            else:
                cursor = connection.cursor(dictionary=True)
                # For MySQL, use DATE_FORMAT
                cursor.execute("SELECT id, username, email, phone, password, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at FROM users")
            
            users = cursor.fetchall()
            cursor.close()

            # Convert SQLite rows to dictionaries for JSON serialization
            if is_sqlite:
                users_list = []
                for row in users:
                    user_dict = {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'phone': row[3],
                        'password': row[4],
                        'created_at': row[5]
                    }
                    users_list.append(user_dict)
                return jsonify({'users': users_list}), 200
            else:
                return jsonify({'users': users}), 200
        finally:
            connection.close()

    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

@app.route('/reset_password', methods=['POST'])
def reset_password():
    """Reset user password"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        new_password = data.get('newPassword')

        # Validate input
        if not username or not email or not new_password:
            return jsonify({'error': 'Username, email, and new password are required'}), 400

        # Query user from database to verify username and email match
        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please check your network connection and database settings.'}), 500

        try:
            # Check if this is a SQLite connection
            is_sqlite = isinstance(connection, sqlite3.Connection)
            
            if is_sqlite:
                cursor = connection.cursor()
            else:
                cursor = connection.cursor(dictionary=True)
            
            if is_sqlite:
                select_query = "SELECT * FROM users WHERE username = ? AND email = ?"
                cursor.execute(select_query, (username, email))
            else:
                select_query = "SELECT * FROM users WHERE username = %s AND email = %s"
                cursor.execute(select_query, (username, email))
            
            user = cursor.fetchone()

            if not user:
                cursor.close()
                return jsonify({'error': 'No user found with that username and email combination'}), 404

            # Hash the new password
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

            # Update the password in the database
            if is_sqlite:
                update_query = "UPDATE users SET password = ? WHERE id = ?"
                cursor.execute(update_query, (hashed_password, user[0]))  # In SQLite, user is tuple, id is at index 0
            else:
                update_query = "UPDATE users SET password = %s WHERE id = %s"
                cursor.execute(update_query, (hashed_password, user['id']))
            
            connection.commit()
            cursor.close()
            return jsonify({'message': 'Password reset successful'}), 200
        finally:
            connection.close()

    except Exception as e:
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500


if __name__ == '__main__':
    # Initialize database
    initialize_database()
    # Run the Flask application
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
