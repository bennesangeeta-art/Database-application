import requests
import json

# Test the registration endpoint with various validation scenarios
BASE_URL = 'http://localhost:5000'

print("Testing registration without required fields...")
# Test registration without username (should fail)
test_data_missing_username = {
    'email': 'test@example.com',
    'phone': '+1234567890',
    'password': 'testpassword123',
    'confirmPassword': 'testpassword123'
}

try:
    response = requests.post(f'{BASE_URL}/register', json=test_data_missing_username)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("✓ Validation correctly rejected missing username")
    else:
        print("✗ Validation did not reject missing username")
except Exception as e:
    print(f"Error during validation test: {e}")

print("\nTesting registration with mismatched passwords...")
# Test registration with mismatched passwords (should fail)
test_data_mismatched_passwords = {
    'username': 'testuser3',
    'email': 'test3@example.com',
    'phone': '+1111111111',
    'password': 'testpassword123',
    'confirmPassword': 'differentpassword'
}

try:
    response = requests.post(f'{BASE_URL}/register', json=test_data_mismatched_passwords)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("✓ Validation correctly rejected mismatched passwords")
    else:
        print("✗ Validation did not reject mismatched passwords")
except Exception as e:
    print(f"Error during validation test: {e}")

print("\nTesting registration with duplicate username (should fail)...")
# Test registration with duplicate username (should fail)
test_data_duplicate = {
    'username': 'testuser1',  # This user was created in previous tests
    'email': 'duplicate@example.com',
    'phone': '+2222222222',
    'password': 'testpassword123',
    'confirmPassword': 'testpassword123'
}

try:
    response = requests.post(f'{BASE_URL}/register', json=test_data_duplicate)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 400:
        print("✓ Validation correctly rejected duplicate username")
    else:
        print("✗ Validation did not reject duplicate username")
except Exception as e:
    print(f"Error during validation test: {e}")

print("\nTesting successful registration with phone number...")
# Test successful registration with phone number
test_data_success = {
    'username': 'testuser4',
    'email': 'test4@example.com',
    'phone': '+3333333333',
    'password': 'testpassword789',
    'confirmPassword': 'testpassword789'
}

try:
    response = requests.post(f'{BASE_URL}/register', json=test_data_success)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✓ Successful registration with phone number accepted")
    else:
        print("✗ Successful registration with phone number failed")
except Exception as e:
    print(f"Error during successful registration test: {e}")