"""
Simple test to verify email service has no syntax errors
"""
import sys
import ast

# Read the email service file
with open('app/services/email_service.py', 'r') as f:
    code = f.read()

# Try to parse it
try:
    ast.parse(code)
    print("✅ email_service.py has valid Python syntax")
except SyntaxError as e:
    print(f"❌ Syntax error in email_service.py: {e}")
    sys.exit(1)

# Read the auth service file
with open('app/services/auth_service.py', 'r') as f:
    code = f.read()

# Try to parse it
try:
    ast.parse(code)
    print("✅ auth_service.py has valid Python syntax")
except SyntaxError as e:
    print(f"❌ Syntax error in auth_service.py: {e}")
    sys.exit(1)

# Read the security file
with open('app/core/security.py', 'r') as f:
    code = f.read()

# Try to parse it
try:
    ast.parse(code)
    print("✅ security.py has valid Python syntax")
except SyntaxError as e:
    print(f"❌ Syntax error in security.py: {e}")
    sys.exit(1)

print("\n✅ All files have valid syntax!")
print("The code should deploy successfully to Render.")
