import requests
import json

# Test the registration endpoint with phone number
BASE_URL = 'http://localhost:5000'

# Test data 1
test_data1 = {
    'username': 'testuser1',
    'email': 'test1@example.com',
    'phone': '+1234567890',
    'password': 'testpassword123',
    'confirmPassword': 'testpassword123'
}

print("Testing first registration with phone number...")
try:
    response = requests.post(f'{BASE_URL}/register', json=test_data1)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✓ First registration with phone number successful!")
    else:
        print("✗ First registration failed")
except Exception as e:
    print(f"Error during first registration test: {e}")

# Test data 2
test_data2 = {
    'username': 'testuser2',
    'email': 'test2@example.com',
    'phone': '+0987654321',
    'password': 'testpassword456',
    'confirmPassword': 'testpassword456'
}

print("\nTesting second registration with phone number...")
try:
    response = requests.post(f'{BASE_URL}/register', json=test_data2)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✓ Second registration with phone number successful!")
    else:
        print("✗ Second registration failed")
except Exception as e:
    print(f"Error during second registration test: {e}")

print("\nTesting login with first user...")
login_data1 = {
    'username': 'testuser1',
    'password': 'testpassword123'
}

try:
    response = requests.post(f'{BASE_URL}/login', json=login_data1)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✓ Login with first user successful!")
    else:
        print("✗ Login with first user failed")
except Exception as e:
    print(f"Error during first login test: {e}")

print("\nTesting login with second user...")
login_data2 = {
    'username': 'testuser2',
    'password': 'testpassword456'
}

try:
    response = requests.post(f'{BASE_URL}/login', json=login_data2)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✓ Login with second user successful!")
    else:
        print("✗ Login with second user failed")
except Exception as e:
    print(f"Error during second login test: {e}")