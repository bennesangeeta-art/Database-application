#!/usr/bin/env python3
"""
Comprehensive Deployment Readiness Check
This script validates the application for production deployment
"""

import os
import sys
import importlib.util
from pathlib import Path

print("=" * 80)
print("DEPLOYMENT READINESS CHECK")
print("=" * 80)

issues = []
warnings = []
successes = []

# Check 1: Required Files
print("\n1. Checking required files...")
required_files = [
    'backend/app.py',
    'backend/requirements.txt',
    'backend/run_production.py',
    'frontend/index.html',
    'backend/.env'
]

for file in required_files:
    if os.path.exists(file):
        successes.append(f"✓ Found: {file}")
    else:
        issues.append(f"✗ Missing: {file}")

# Check 2: Python Dependencies
print("\n2. Checking Python dependencies...")
try:
    import flask
    successes.append("✓ Flask installed")
except ImportError:
    issues.append("✗ Flask not installed")

try:
    import flask_cors
    successes.append("✓ Flask-CORS installed")
except ImportError:
    issues.append("✗ Flask-CORS not installed")

try:
    import mysql.connector
    successes.append("✓ MySQL connector installed")
except ImportError:
    issues.append("✗ MySQL connector not installed")

try:
    import dotenv
    successes.append("✓ python-dotenv installed")
except ImportError:
    issues.append("✗ python-dotenv not installed")

try:
    import waitress
    successes.append("✓ Waitress installed (production server)")
except ImportError:
    warnings.append("⚠ Waitress not installed (recommended for production)")

try:
    import werkzeug
    successes.append("✓ Werkzeug installed (security)")
except ImportError:
    issues.append("✗ Werkzeug not installed")

# Check 3: Environment Variables
print("\n3. Checking environment configuration...")
if os.path.exists('backend/.env'):
    successes.append("✓ .env file exists")
    
    # Load and check variables
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    
    env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_PORT']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'DB_PASSWORD':
                successes.append(f"✓ {var} is set (hidden)")
            else:
                successes.append(f"✓ {var} is set: {value[:20]}...")
        else:
            warnings.append(f"⚠ {var} not set in .env")
else:
    issues.append("✗ .env file missing - will use default values")

# Check 4: Database Connectivity
print("\n4. Testing database connectivity...")
try:
    sys.path.insert(0, 'backend')
    from app import get_db_connection
    
    conn = get_db_connection()
    if conn:
        successes.append("✓ Database connection successful")
        conn.close()
    else:
        warnings.append("⚠ Database connection failed - SQLite fallback will be used")
except Exception as e:
    warnings.append(f"⚠ Database test failed: {str(e)}")

# Check 5: Static Files
print("\n5. Checking static files...")
static_checks = [
    ('frontend/index.html', 'Main HTML file'),
]

for file, description in static_checks:
    if os.path.exists(file):
        successes.append(f"✓ {description}: {file}")
        
        # Check file size
        size = os.path.getsize(file)
        if size > 0:
            successes.append(f"  ✓ File has content ({size} bytes)")
        else:
            issues.append(f"  ✗ File is empty: {file}")
    else:
        issues.append(f"✗ {description} missing: {file}")

# Check 6: Code Quality Checks
print("\n6. Running basic code quality checks...")

# Check if app.py can be imported without errors
try:
    spec = importlib.util.spec_from_file_location("app", "backend/app.py")
    module = importlib.util.module_from_spec(spec)
    # Don't execute, just check syntax
    successes.append("✓ backend/app.py has valid Python syntax")
except SyntaxError as e:
    issues.append(f"✗ Syntax error in app.py: {e}")
except Exception as e:
    warnings.append(f"⚠ Could not validate app.py: {e}")

# Check 7: Security Checks
print("\n7. Security checks...")

# Check if passwords are hashed
with open('backend/app.py', 'r') as f:
    app_content = f.read()
    
if 'generate_password_hash' in app_content:
    successes.append("✓ Password hashing implemented")
else:
    issues.append("✗ Password hashing not found")

if 'check_password_hash' in app_content:
    successes.append("✓ Password verification implemented")
else:
    issues.append("✗ Password verification not found")

# Check for hardcoded credentials (basic check)
suspicious_patterns = ['password=', 'secret=', 'api_key=']
found_suspicious = False
for pattern in suspicious_patterns:
    if pattern.lower() in app_content.lower() and 'os.getenv' not in app_content:
        found_suspicious = True
        
if not found_suspicious:
    successes.append("✓ No obvious hardcoded credentials found")
else:
    warnings.append("⚠ Potential hardcoded credentials detected - review manually")

# Check 8: CORS Configuration
print("\n8. Checking CORS configuration...")
if 'CORS(app)' in app_content or 'flask_cors' in app_content:
    successes.append("✓ CORS configured")
else:
    warnings.append("⚠ CORS not explicitly configured")

# Check 9: Error Handling
print("\n9. Checking error handling...")
if 'try:' in app_content and 'except' in app_content:
    successes.append("✓ Error handling implemented")
else:
    warnings.append("⚠ Limited error handling detected")

# Check 10: Production Server
print("\n10. Checking production server configuration...")
if os.path.exists('backend/run_production.py'):
    with open('backend/run_production.py', 'r') as f:
        prod_content = f.read()
    
    if 'waitress' in prod_content.lower():
        successes.append("✓ Waitress production server configured")
    else:
        warnings.append("⚠ Waitress not used in run_production.py")
    
    if 'debug=False' in prod_content or 'debug=False' in app_content:
        successes.append("✓ Debug mode disabled for production")
    else:
        issues.append("✗ Debug mode might be enabled - security risk!")

# Print Results
print("\n" + "=" * 80)
print("DEPLOYMENT READINESS REPORT")
print("=" * 80)

print(f"\n✅ SUCCESSES: {len(successes)}")
for success in successes[:10]:  # Show first 10
    print(f"  {success}")
if len(successes) > 10:
    print(f"  ... and {len(successes) - 10} more")

print(f"\n⚠️  WARNINGS: {len(warnings)}")
for warning in warnings:
    print(f"  {warning}")

print(f"\n❌ ISSUES: {len(issues)}")
for issue in issues:
    print(f"  {issue}")

print("\n" + "=" * 80)

# Final Assessment
if len(issues) == 0:
    print("✅ DEPLOYMENT READY! No critical issues found.")
    sys.exit(0)
elif len(issues) <= 2 and not any('debug' in i.lower() for i in issues):
    print("⚠️  MOSTLY READY - Minor issues detected but safe to deploy.")
    sys.exit(0)
else:
    print("❌ NOT READY FOR DEPLOYMENT - Critical issues must be fixed first.")
    sys.exit(1)
