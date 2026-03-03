from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'userdb'),
    'port': int(os.getenv('DB_PORT', 3306)) if os.getenv('DB_PORT') else 3306,
    'ssl_disabled': True,
    'connect_timeout': 10,
    'connection_timeout': 10
}

def get_db_connection():
    """Establish a connection to the MySQL database, with SQLite fallback"""
    try:
        print(f"Attempting MySQL connection to: {db_config['host']}:{db_config['port']}, user: {db_config['user']}, db: {db_config['database']}")
        
        connection = mysql.connector.connect(**db_config)
        print("MySQL connection successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"MySQL connection failed: {err}")
        print("Falling back to SQLite...")
        
        # Fallback to SQLite
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'users_local.db')
            conn = sqlite3.connect(db_path, timeout=20.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
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

        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500

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
        connection.close()

        return jsonify({'message': 'Registration successful'}), 201

    except (mysql.connector.IntegrityError, sqlite3.IntegrityError) as err:
        error_str = str(err)
        if "Duplicate entry" in error_str or "UNIQUE constraint failed" in error_str:
            return jsonify({'error': 'Username or email already exists'}), 400
        else:
            return jsonify({'error': f'Database error: {error_str}'}), 500
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500

        is_sqlite = isinstance(connection, sqlite3.Connection)
        cursor = connection.cursor() if is_sqlite else connection.cursor(dictionary=True)
        
        if is_sqlite:
            select_query = "SELECT * FROM users WHERE username = ?"
            cursor.execute(select_query, (username,))
        else:
            select_query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(select_query, (username,))
        
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user['password'], password):
            return jsonify({
                'message': 'Login successful',
                'username': username
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/users', methods=['POST'])
def get_users():
    """Get all registered users"""
    try:
        data = request.get_json() or {}
        admin_password = data.get('adminPassword')

        if not admin_password or admin_password != os.getenv('DB_PASSWORD'):
            return jsonify({'error': 'Unauthorized: Incorrect admin password'}), 401

        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500

        is_sqlite = isinstance(connection, sqlite3.Connection)
        cursor = connection.cursor() if is_sqlite else connection.cursor(dictionary=True)
        
        if is_sqlite:
            cursor.execute("SELECT id, username, email, phone, password, datetime(created_at) as created_at FROM users")
        else:
            cursor.execute("SELECT id, username, email, phone, password, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') as created_at FROM users")
        
        users = cursor.fetchall()
        cursor.close()
        connection.close()

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

    except Exception as e:
        print(f"Get users error: {str(e)}")
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

@app.route('/reset_password', methods=['POST'])
def reset_password():
    """Reset user password"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        new_password = data.get('newPassword')

        if not username or not email or not new_password:
            return jsonify({'error': 'Username, email, and new password are required'}), 400

        connection = get_db_connection()
        if connection is None:
            return jsonify({'error': 'Database connection failed. Please try again later.'}), 500

        is_sqlite = isinstance(connection, sqlite3.Connection)
        cursor = connection.cursor() if is_sqlite else connection.cursor(dictionary=True)
        
        if is_sqlite:
            select_query = "SELECT * FROM users WHERE username = ? AND email = ?"
            cursor.execute(select_query, (username, email))
        else:
            select_query = "SELECT * FROM users WHERE username = %s AND email = %s"
            cursor.execute(select_query, (username, email))
        
        user = cursor.fetchone()

        if not user:
            cursor.close()
            connection.close()
            return jsonify({'error': 'No user found with that username and email combination'}), 404

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        if is_sqlite:
            update_query = "UPDATE users SET password = ? WHERE id = ?"
            cursor.execute(update_query, (hashed_password, user[0]))
        else:
            update_query = "UPDATE users SET password = %s WHERE id = %s"
            cursor.execute(update_query, (hashed_password, user['id']))
        
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Password reset successful'}), 200

    except Exception as e:
        print(f"Password reset error: {str(e)}")
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
