#!/usr/bin/env python3
"""
Pulse App Setup Test Script
Verifies that both backend and frontend are properly configured and can communicate
"""

import subprocess
import time
import requests
import json
import os
import sys
from pathlib import Path

def check_python_dependencies():
    """Check if required Python packages are installed"""
    print("🐍 Checking Python dependencies...")
    
    required_packages = [
        'flask', 'flask-cors', 'pymongo', 'bcrypt', 
        'pyjwt', 'python-dotenv', 'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r backend/requirements.txt")
        return False
    
    print("✅ All Python dependencies are installed")
    return True

def check_backend_config():
    """Check backend configuration"""
    print("\n🔧 Checking backend configuration...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Check app.py exists
    app_file = backend_dir / "app.py"
    if not app_file.exists():
        print("❌ app.py not found in backend directory")
        return False
    print("  ✅ app.py found")
    
    # Check .env file
    env_file = backend_dir / ".env"
    if env_file.exists():
        print("  ✅ .env file found")
    else:
        print("  ⚠️ .env file not found (will use defaults)")
    
    return True

def check_frontend_config():
    """Check frontend configuration"""
    print("\n🎨 Checking frontend configuration...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check package.json
    package_file = frontend_dir / "package.json"
    if not package_file.exists():
        print("❌ package.json not found in frontend directory")
        return False
    print("  ✅ package.json found")
    
    # Check node_modules
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("  ✅ node_modules found")
    else:
        print("  ❌ node_modules not found")
        print("  Run: cd frontend && npm install")
        return False
    
    return True

def test_backend_startup():
    """Test if backend starts without errors"""
    print("\n🚀 Testing backend startup...")
    
    try:
        # Try to import the app to check for syntax errors
        sys.path.insert(0, str(Path("backend").absolute()))
        
        # Change to backend directory
        original_cwd = os.getcwd()
        os.chdir("backend")
        
        try:
            import app
            print("  ✅ Backend imports successfully")
            
            # Test basic functionality
            with app.app.test_client() as client:
                response = client.get('/')
                if response.status_code == 200:
                    print("  ✅ Basic route works")
                else:
                    print(f"  ❌ Basic route failed: {response.status_code}")
                    return False
                
                # Test health endpoint
                response = client.get('/api/health')
                if response.status_code == 200:
                    print("  ✅ Health endpoint works")
                else:
                    print(f"  ❌ Health endpoint failed: {response.status_code}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Backend startup failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"  ❌ Failed to test backend: {e}")
        return False

def test_live_backend():
    """Test if backend is running and responding"""
    print("\n🌐 Testing live backend connection...")
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Backend is running: {data.get('message', 'OK')}")
            return True
        else:
            print(f"  ❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ⚠️ Backend is not running")
        print("  Start it with: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"  ❌ Backend test failed: {e}")
        return False

def main():
    print("🔍 Pulse App Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check Python dependencies
    if not check_python_dependencies():
        all_good = False
    
    # Check backend configuration
    if not check_backend_config():
        all_good = False
    
    # Check frontend configuration
    if not check_frontend_config():
        all_good = False
    
    # Test backend startup
    if not test_backend_startup():
        all_good = False
    
    # Test live backend
    backend_running = test_live_backend()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if all_good:
        print("✅ Configuration is correct")
    else:
        print("❌ Configuration issues found")
    
    if backend_running:
        print("✅ Backend is running and responding")
    else:
        print("❌ Backend is not running")
    
    print("\n🚀 NEXT STEPS:")
    
    if not all_good:
        print("1. Fix configuration issues above")
    
    if not backend_running:
        print("2. Start backend: cd backend && python app.py")
    
    print("3. Start frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:5173 in your browser")
    print("5. Test the network connectivity using the NetworkTest component")
    
    if all_good and backend_running:
        print("\n🎉 Everything looks good! Your Pulse app should work correctly.")
        return 0
    else:
        print("\n⚠️ Please fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())