import requests
import json

# Test the registration endpoint with phone number
BASE_URL = 'http://localhost:5000'

# Test data with new user
test_data = {
    'username': 'finaltestuser',
    'email': 'finaltest@example.com',
    'phone': '+9876543210',
    'password': 'finalpass123',
    'confirmPassword': 'finalpass123'
}

print("Testing registration with phone number...")
try:
    response = requests.post(f'{BASE_URL}/register', json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✓ Registration with phone number successful!")
    else:
        print("✗ Registration failed")
except Exception as e:
    print(f"Error during registration test: {e}")

print("\nTesting login...")
login_data = {
    'username': 'finaltestuser',
    'password': 'finalpass123'
}

try:
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✓ Login successful!")
    else:
        print("✗ Login failed")
except Exception as e:
    print(f"Error during login test: {e}")

print("\nTesting /users endpoint with correct admin password...")
try:
    import os
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    admin_password = os.getenv('DB_PASSWORD')
    response = requests.post(f'{BASE_URL}/users', json={'adminPassword': admin_password})
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        users_count = len(response.json()['users'])
        print(f"Response: {users_count} users found")
    else:
        print("Failed to get users")
    
    if response.status_code == 200:
        print("✓ Users endpoint working correctly!")
    else:
        print("✗ Users endpoint failed")
except Exception as e:
    print(f"Error during users test: {e}")

print("\nTesting /reset_password endpoint...")
reset_data = {
    'username': 'finaltestuser',
    'email': 'finaltest@example.com',
    'newPassword': 'updatedpassword123'
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

print("\nTesting login with updated password...")
login_data = {
    'username': 'finaltestuser',
    'password': 'updatedpassword123'
}

try:
    response = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✓ Login with updated password successful!")
    else:
        print("✗ Login with updated password failed")
except Exception as e:
    print(f"Error during login test: {e}")

print("\nAll tests completed!")