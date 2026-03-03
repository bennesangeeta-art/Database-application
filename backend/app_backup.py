from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend')
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
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """Establish a connection to the MySQL database"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def initialize_database():
    """Initialize the database and create users table if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database first)
        temp_config = db_config.copy()
        temp_config.pop('database', None)  # Remove database name temporarily
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        connection.commit()
        
        # Now connect to the specific database
        connection.database = db_config['database']
        
        # Check if phone column exists, if not, add it
        check_column_query = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'phone'
        """
        cursor.execute(check_column_query, (db_config['database'],))
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
        
        print("Database initialized successfully")
        
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

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
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor()
        insert_query = "INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (username, email, phone, hashed_password))
        connection.commit()

        # Close connections
        cursor.close()
        connection.close()

        return jsonify({'message': 'Registration successful'}), 201

    except mysql.connector.IntegrityError as err:
        # Handle duplicate entry errors
        if "Duplicate entry" in str(err):
            return jsonify({'error': 'Username or email already exists'}), 400
        else:
            return jsonify({'error': f'Database error: {str(err)}'}), 500
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
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        select_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(select_query, (username,))
        user = cursor.fetchone()

        # Close connections
        cursor.close()
        connection.close()

        # Check if user exists and password is correct
        if user and check_password_hash(user['password'], password):
            return jsonify({
                'message': 'Login successful',
                'username': username
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database
    initialize_database()
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)