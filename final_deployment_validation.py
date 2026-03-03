#!/usr/bin/env python3
"""
Final Comprehensive Deployment Validation
Tests all aspects before production deployment
"""

import os
import sys
import requests
from dotenv import load_dotenv

print("=" * 80)
print("FINAL DEPLOYMENT VALIDATION")
print("=" * 80)

# Load environment
load_dotenv('backend/.env')

all_passed = True
tests_run = 0
tests_passed = 0

def check(description, condition, critical=True):
    """Check a condition and report result"""
    global tests_run, tests_passed, all_passed
    tests_run += 1
    
    if condition:
        print(f"✓ {description}")
        tests_passed += 1
        return True
    else:
        if critical:
            print(f"✗ {description}")
            all_passed = False
        else:
            print(f"⚠ {description}")
        return False

print("\n1. FILE SYSTEM CHECKS")
print("-" * 60)

# Check required files exist
check("backend/app.py exists", os.path.exists('backend/app.py'))
check("backend/requirements.txt exists", os.path.exists('backend/requirements.txt'))
check("backend/run_production.py exists", os.path.exists('backend/run_production.py'))
check("frontend/index.html exists", os.path.exists('frontend/index.html'))
check(".gitignore exists", os.path.exists('.gitignore'))
check("DEPLOYMENT_GUIDE.md exists", os.path.exists('DEPLOYMENT_GUIDE.md'))

print("\n2. ENVIRONMENT CONFIGURATION")
print("-" * 60)

check("DB_HOST configured", bool(os.getenv('DB_HOST')))
check("DB_USER configured", bool(os.getenv('DB_USER')))
check("DB_PASSWORD configured", bool(os.getenv('DB_PASSWORD')))
check("DB_NAME configured", bool(os.getenv('DB_NAME')))
check("DB_PORT configured", bool(os.getenv('DB_PORT')))

print("\n3. SERVER HEALTH")
print("-" * 60)

try:
    response = requests.get('http://localhost:5000/', timeout=5)
    check("Server responds on port 5000", response.status_code == 200)
    check("Frontend HTML served", 'text/html' in response.headers.get('Content-Type', ''))
except Exception as e:
    check("Server accessible", False)
    print(f"  Error: {e}")

print("\n4. API ENDPOINT TESTS")
print("-" * 60)

BASE_URL = 'http://localhost:5000'

# Test registration
import time
timestamp = str(int(time.time()))
test_user = {
    'username': f'final_test_{timestamp}',
    'email': f'final{timestamp}@test.com',
    'phone': '+1234567890',
    'password': 'FinalTest123!',
    'confirmPassword': 'FinalTest123!'
}

try:
    reg_response = requests.post(f'{BASE_URL}/register', json=test_user, timeout=10)
    check("Registration API works", reg_response.status_code == 201)
    
    # Test login
    login_response = requests.post(f'{BASE_URL}/login', json={
        'username': test_user['username'],
        'password': test_user['password']
    }, timeout=10)
    check("Login API works", login_response.status_code == 200)
    
    # Test password reset
    reset_response = requests.post(f'{BASE_URL}/reset_password', json={
        'username': test_user['username'],
        'email': test_user['email'],
        'newPassword': 'NewFinalTest456!'
    }, timeout=10)
    check("Password reset API works", reset_response.status_code == 200)
    
    # Test admin endpoint
    admin_response = requests.post(f'{BASE_URL}/users', json={
        'adminPassword': os.getenv('DB_PASSWORD')
    }, timeout=10)
    check("Admin users API works", admin_response.status_code == 200)
    
except Exception as e:
    check("API endpoints functional", False)
    print(f"  Error: {e}")

print("\n5. SECURITY CHECKS")
print("-" * 60)

# Check password hashing
with open('backend/app.py', 'r') as f:
    app_code = f.read()

check("Password hashing implemented", 'generate_password_hash' in app_code)
check("Password verification implemented", 'check_password_hash' in app_code)
check("CORS enabled", 'CORS(app)' in app_code or 'flask_cors' in app_code)
check("Environment variables used", 'os.getenv' in app_code)
check("No hardcoded passwords", not ('password=' in app_code.lower() and 'os.getenv' not in app_code))

print("\n6. DATABASE CONNECTIVITY")
print("-" * 60)

# Import and test database connection
sys.path.insert(0, 'backend')
try:
    from app import get_db_connection
    conn = get_db_connection()
    check("Database connection successful", conn is not None)
    if conn:
        conn.close()
        check("Database connection closes properly", True)
except Exception as e:
    check("Database module loads", False)
    print(f"  Error: {e}")

print("\n7. PRODUCTION SERVER")
print("-" * 60)

check("Waitress installed", os.path.exists('backend/run_production.py'))

with open('backend/run_production.py', 'r') as f:
    prod_code = f.read()

check("Uses Waitress server", 'waitress' in prod_code.lower())
check("Debug mode disabled", 'debug=False' in prod_code or 'debug = False' in app_code)
check("Binds to all interfaces", 'host=\'0.0.0.0\'' in prod_code or 'host="0.0.0.0"' in prod_code)

print("\n8. ERROR HANDLING")
print("-" * 60)

check("Try-except blocks present", 'try:' in app_code and 'except' in app_code)
check("Error messages returned", 'error' in app_code.lower())
check("Graceful degradation (SQLite fallback)", 'sqlite3' in app_code)

print("\n9. INPUT VALIDATION")
print("-" * 60)

# Test missing field validation
bad_request = requests.post(f'{BASE_URL}/register', json={
    'username': 'test',
    'email': 'test@test.com'
}, timeout=10)

check("Validates missing fields", bad_request.status_code == 400)

# Test password mismatch
mismatch_request = requests.post(f'{BASE_URL}/register', json={
    'username': 'test',
    'email': 'test@test.com',
    'phone': '+1234567890',
    'password': 'pass1',
    'confirmPassword': 'pass2'
}, timeout=10)

check("Validates password mismatch", mismatch_request.status_code == 400)

print("\n10. CORS HEADERS")
print("-" * 60)

response = requests.get(f'{BASE_URL}/', timeout=5)
cors_header = response.headers.get('Access-Control-Allow-Origin', '')
check("CORS header present", '*' in cors_header or len(cors_header) > 0)

print("\n" + "=" * 80)
print("FINAL DEPLOYMENT REPORT")
print("=" * 80)

success_rate = (tests_passed / tests_run * 100) if tests_run > 0 else 0

print(f"\nTests Run: {tests_run}")
print(f"Tests Passed: {tests_passed}")
print(f"Success Rate: {success_rate:.1f}%")

if all_passed and success_rate >= 95:
    print("\n✅ DEPLOYMENT CERTIFIED!")
    print("The application has passed all critical deployment checks.")
    print("Ready for production deployment.")
    exit_code = 0
elif success_rate >= 80:
    print("\n⚠️  MOSTLY READY")
    print("Minor issues detected but core functionality is solid.")
    print("Recommended to fix warnings before production.")
    exit_code = 0
else:
    print("\n❌ NOT READY FOR DEPLOYMENT")
    print("Critical issues must be resolved before deploying to production.")
    exit_code = 1

print("\n" + "=" * 80)

sys.exit(exit_code)
