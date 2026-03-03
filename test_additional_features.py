import requests
import json

# Test the additional endpoints you added
BASE_URL = 'http://localhost:5000'

print("Testing /users endpoint (should fail without admin password)...")
try:
    response = requests.post(f'{BASE_URL}/users', json={})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error during users test: {e}")

print("\nTesting /users endpoint with correct admin password...")
try:
    import os
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    admin_password = os.getenv('DB_PASSWORD')
    response = requests.post(f'{BASE_URL}/users', json={'adminPassword': admin_password})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error during users test: {e}")

print("\nTesting /reset_password endpoint...")
reset_data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'newPassword': 'newpassword123'
}

try:
    response = requests.post(f'{BASE_URL}/reset_password', json=reset_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✓ Password reset successful!")
    else:
        print("✗ Password reset failed")
except Exception as e:
    print(f"Error during password reset test: {e}")

print("\nTesting login with new password...")
login_data = {
    'username': 'testuser',
    'password': 'newpassword123'
}

try:
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✓ Login with new password successful!")
    else:
        print("✗ Login with new password failed")
except Exception as e:
    print(f"Error during login test: {e}")