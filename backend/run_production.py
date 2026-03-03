from waitress import serve
from app import app, initialize_database
import os

if __name__ == '__main__':
    # Initialize database before starting the server
    print("Initializing database...")
    initialize_database()
    
    # Run the application using Waitress
    port = int(os.getenv('PORT', 5000))
    print(f"Starting production server on http://0.0.0.0:{port}")
    serve(app, host='0.0.0.0', port=port)