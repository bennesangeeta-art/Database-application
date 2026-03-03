import requests
import json

# Test the registration endpoint with phone number
BASE_URL = 'http://localhost:5000'

# Test data
test_data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'phone': '+1234567890',
    'password': 'testpass123',
    'confirmPassword': 'testpass123'
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
    'username': 'testuser',
    'password': 'testpass123'
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