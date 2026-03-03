import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Extract config values
host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
database = os.getenv('DB_NAME', 'userdb')
port = int(os.getenv('DB_PORT', 3306))

print(f"Attempting connection to: {host}:{port}, user: {user}, db: {database}")

try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        ssl_disabled=True
    )
    print('PyMySQL Connection successful!')
    connection.close()
except Exception as err:
    print(f"Error connecting to MySQL with PyMySQL: {err}")