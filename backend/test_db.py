import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT'))
}

print('Testing connection with config:', config)

try:
    conn = mysql.connector.connect(**config)
    print('Connection successful!')
    conn.close()
except Exception as e:
    print('Connection failed:', e)