#!/usr/bin/env python3
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✓ App imported successfully")
    print("✓ Starting server on http://127.0.0.1:5000")
    print("✓ Registration endpoint: POST /api/auth/register")
    print("✓ Login endpoint: POST /api/auth/login")
    print("✓ Press Ctrl+C to stop")
    app.run(debug=True, port=5000, host='127.0.0.1')
except Exception as e:
    print(f"✗ Error starting server: {e}")
    sys.exit(1)