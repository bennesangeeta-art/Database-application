import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'userdb'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def check_users():
    try:
        print(f"Connecting to database '{db_config['database']}' at {db_config['host']}...")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT id, username, email, phone, created_at FROM users")
        users = cursor.fetchall()
        
        print("\n--- Users in Database ---")
        if not users:
            print("No users found.")
        else:
            for user in users:
                print(f"ID: {user['id']} | Username: {user['username']} | Email: {user['email']} | Phone: {user['phone']} | Created: {user['created_at']}")
                
        print("-------------------------\n")
                
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    check_users()
