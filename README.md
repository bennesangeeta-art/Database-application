# User Authentication System

This application consists of a frontend and backend for user registration and login functionality.

## Backend (Flask)

The backend is built with Flask and uses SQLite for data storage.

### Features
- User registration with password hashing
- User login with credential verification
- RESTful API endpoints

### Endpoints
- `POST /register` - Register a new user
- `POST /login` - Authenticate user login

### Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

The backend will run on `http://localhost:5000`.

## Frontend (HTML/CSS/JavaScript)

The frontend provides a complete user interface for registration, login, and dashboard functionality.

### Features
- Registration page with validation
- Login page
- Dashboard showing welcome message
- Responsive design

### Setup
Simply open `frontend/index.html` in a web browser.

### API Connection
The frontend connects to the backend API at `http://localhost:5000`.

## How to Use
1. Start the backend server
2. Open the frontend in a browser
3. Register a new account
4. Log in with your credentials
5. View the dashboard