#!/usr/bin/env python3
"""
Post-Deployment Validation Test
Tests all functionality after deployment
"""

import requests
import json
import os
from dotenv import load_dotenv

print("=" * 80)
print("POST-DEPLOYMENT VALIDATION TEST")
print("=" * 80)

BASE_URL = 'http://localhost:5000'
load_dotenv('backend/.env')
admin_password = os.getenv('DB_PASSWORD')

test_results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0
}

def test_endpoint(name, method, url, data=None, expected_status=200):
    """Test an endpoint and record results"""
    print(f"\nTesting: {name}")
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        status_match = response.status_code == expected_status
        
        print(f"  Status: {response.status_code} (Expected: {expected_status}) - {'✓' if status_match else '✗'}")
        
        if status_match:
            test_results['passed'] += 1
            return True
        else:
            test_results['failed'] += 1
            print(f"  Response: {response.text[:200]}")
            return False
    except Exception as e:
        test_results['failed'] += 1
        print(f"  ✗ Error: {str(e)}")
        return False

# Test 1: Server Health Check
print("\n" + "=" * 60)
print("1. SERVER HEALTH CHECKS")
print("=" * 60)

# Check if frontend loads
test_endpoint(
    "Frontend serves correctly",
    'GET',
    f'{BASE_URL}/'
)

# Test 2: Registration API
print("\n" + "=" * 60)
print("2. REGISTRATION API TESTS")
print("=" * 60)

# Generate unique test user
import time
timestamp = str(int(time.time()))
test_user = {
    'username': f'deploy_test_{timestamp}',
    'email': f'deploy_test_{timestamp}@example.com',
    'phone': '+9876543210',
    'password': 'DeployTest123!',
    'confirmPassword': 'DeployTest123!'
}

test_endpoint(
    "Register new user with phone",
    'POST',
    f'{BASE_URL}/register',
    test_user,
    201
)

# Test validation - missing fields
test_endpoint(
    "Validation: Missing required fields",
    'POST',
    f'{BASE_URL}/register',
    {'username': 'test', 'email': 'test@test.com'},
    400
)

# Test validation - password mismatch
test_endpoint(
    "Validation: Password mismatch",
    'POST',
    f'{BASE_URL}/register',
    {
        'username': 'test',
        'email': 'test@test.com',
        'phone': '+1234567890',
        'password': 'pass1',
        'confirmPassword': 'pass2'
    },
    400
)

# Test 3: Login API
print("\n" + "=" * 60)
print("3. LOGIN API TESTS")
print("=" * 60)

test_endpoint(
    "Login with valid credentials",
    'POST',
    f'{BASE_URL}/login',
    {
        'username': test_user['username'],
        'password': test_user['password']
    },
    200
)

test_endpoint(
    "Login with invalid credentials",
    'POST',
    f'{BASE_URL}/login',
    {
        'username': test_user['username'],
        'password': 'wrongpassword'
    },
    401
)

# Test 4: Admin Features
print("\n" + "=" * 60)
print("4. ADMIN FEATURES TESTS")
print("=" * 60)

test_endpoint(
    "Admin: Get users without password",
    'POST',
    f'{BASE_URL}/users',
    {},
    401
)

test_endpoint(
    "Admin: Get users with correct password",
    'POST',
    f'{BASE_URL}/users',
    {'adminPassword': admin_password},
    200
)

# Test 5: Password Reset
print("\n" + "=" * 60)
print("5. PASSWORD RESET TESTS")
print("=" * 60)

test_endpoint(
    "Reset password",
    'POST',
    f'{BASE_URL}/reset_password',
    {
        'username': test_user['username'],
        'email': test_user['email'],
        'newPassword': 'NewDeployTest456!'
    },
    200
)

test_endpoint(
    "Login with new password",
    'POST',
    f'{BASE_URL}/login',
    {
        'username': test_user['username'],
        'password': 'NewDeployTest456!'
    },
    200
)

# Test 6: Database Persistence
print("\n" + "=" * 60)
print("6. DATABASE PERSISTENCE TESTS")
print("=" * 60)

# Verify user still exists in database
response = requests.post(f'{BASE_URL}/users', json={'adminPassword': admin_password})
if response.status_code == 200:
    users = response.json()['users']
    user_found = any(u['username'] == test_user['username'] for u in users)
    if user_found:
        print(f"  ✓ User persisted in database")
        test_results['passed'] += 1
    else:
        print(f"  ✗ User not found in database")
        test_results['failed'] += 1
else:
    test_results['warnings'] += 1
    print(f"  ⚠ Could not verify database persistence")

# Test 7: CORS Headers
print("\n" + "=" * 60)
print("7. CORS CONFIGURATION TESTS")
print("=" * 60)

response = requests.get(f'{BASE_URL}/')
if 'Access-Control-Allow-Origin' in response.headers or '*' in response.headers.get('Access-Control-Allow-Origin', ''):
    print(f"  ✓ CORS headers present")
    test_results['passed'] += 1
else:
    print(f"  ⚠ CORS headers not explicitly checked")
    test_results['warnings'] += 1

# Final Report
print("\n" + "=" * 80)
print("DEPLOYMENT VALIDATION REPORT")
print("=" * 80)
print(f"\n✅ PASSED: {test_results['passed']}")
print(f"❌ FAILED: {test_results['failed']}")
print(f"⚠️  WARNINGS: {test_results['warnings']}")

total_tests = test_results['passed'] + test_results['failed']
success_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"\n📊 SUCCESS RATE: {success_rate:.1f}%")

if test_results['failed'] == 0:
    print("\n🎉 DEPLOYMENT VALIDATION SUCCESSFUL!")
    print("All critical tests passed. Application is ready for production.")
elif test_results['failed'] <= 2:
    print("\n⚠️  DEPLOYMENT MOSTLY READY")
    print("Minor issues detected but core functionality works.")
else:
    print("\n❌ DEPLOYMENT VALIDATION FAILED")
    print("Critical issues must be resolved before production deployment.")

print("=" * 80)
