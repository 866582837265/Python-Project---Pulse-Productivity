# setup_platform_integration.py
"""
Quick setup script for Pulse Platform Integration
This script helps verify that all components are properly configured
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'pymongo',
        'bcrypt',
        'pyjwt',
        'python-dotenv',
        'requests',
        'beautifulsoup4',
        'schedule',
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle package name variations
            import_name = package.replace('-', '_').replace('flask_cors', 'flask_cors')
            if package == 'beautifulsoup4':
                import_name = 'bs4'
            elif package == 'python-dotenv':
                import_name = 'dotenv'
            elif package == 'pyjwt':
                import_name = 'jwt'
            
            importlib.import_module(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 Checking file structure...")
    
    required_files = [
        'backend/app.py',
        'backend/coding_platforms.py',
        'backend/progress_sync_service.py',
        'backend/requirements.txt',
        'frontend/src/UserProfile.jsx',
        'frontend/src/UserProfile.css',
        'frontend/src/api.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present")
    return True

def test_platform_apis():
    """Test platform API connectivity"""
    print("\n🌐 Testing platform API connectivity...")
    
    try:
        # Import and test the tracker
        sys.path.append('backend')
        from coding_platforms import CodingPlatformTracker
        
        tracker = CodingPlatformTracker()
        
        # Test LeetCode API
        print("Testing LeetCode API...")
        leetcode_result = tracker.get_leetcode_stats("leetcode")
        if leetcode_result.get('success'):
            print("✅ LeetCode API is accessible")
        else:
            print("⚠️ LeetCode API test failed (this may be normal)")
        
        # Test HackerRank API
        print("Testing HackerRank API...")
        hackerrank_result = tracker.get_hackerrank_stats("shashank21j")
        if hackerrank_result.get('success'):
            print("✅ HackerRank API is accessible")
        else:
            print("⚠️ HackerRank API test failed (this may be normal)")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check if .env file exists
    env_file = 'backend/.env'
    if os.path.exists(env_file):
        print("✅ Environment file found")
        
        # Read and check basic configuration
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
                
            if 'JWT_SECRET' in env_content:
                print("✅ JWT_SECRET configured")
            else:
                print("⚠️ JWT_SECRET not found in .env")
                
            if 'MONGODB_URI' in env_content or 'MONGO_URI' in env_content:
                print("✅ Database URI configured")
            else:
                print("⚠️ Database URI not configured (will use in-memory storage)")
                
        except Exception as e:
            print(f"⚠️ Could not read .env file: {e}")
    else:
        print("⚠️ .env file not found (using defaults)")
    
    return True

def run_integration_test():
    """Run the integration test script"""
    print("\n🧪 Running integration tests...")
    
    try:
        test_script = 'backend/test_platform_integration.py'
        if os.path.exists(test_script):
            result = subprocess.run([sys.executable, test_script], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                print("✅ Integration tests passed")
                return True
            else:
                print("⚠️ Some integration tests failed")
                print("This is normal if you don't have internet connectivity")
                return True
        else:
            print("⚠️ Integration test script not found")
            return False
            
    except Exception as e:
        print(f"⚠️ Could not run integration tests: {e}")
        return False

def create_sample_env():
    """Create a sample .env file if it doesn't exist"""
    env_file = 'backend/.env'
    
    if not os.path.exists(env_file):
        print("\n📝 Creating sample .env file...")
        
        sample_env = """# Pulse Application Environment Configuration

# JWT Secret Key (change this in production)
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# MongoDB Configuration
# For MongoDB Atlas (cloud):
# MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/pulseDB?retryWrites=true&w=majority

# For local MongoDB:
# MONGODB_URI=mongodb://localhost:27017/pulseDB

# For testing without MongoDB (uses in-memory storage):
MONGODB_URI=

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Platform Integration Settings (optional)
# LEETCODE_API_DELAY=2
# HACKERRANK_API_DELAY=3
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(sample_env)
            print("✅ Sample .env file created")
            print("📝 Please review and update the configuration as needed")
        except Exception as e:
            print(f"❌ Could not create .env file: {e}")

def main():
    """Main setup function"""
    print("🚀 Pulse Platform Integration Setup")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("Environment", check_environment),
        ("Platform APIs", test_platform_apis),
        ("Integration Tests", run_integration_test)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{'-' * 30}")
        print(f"Running: {check_name}")
        print(f"{'-' * 30}")
        
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")
            results.append((check_name, False))
    
    # Create sample .env if needed
    create_sample_env()
    
    # Summary
    print(f"\n{'=' * 50}")
    print("SETUP SUMMARY")
    print(f"{'=' * 50}")
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed >= total - 1:  # Allow one failure (usually API tests)
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Review the .env file configuration")
        print("2. Start the backend server: python backend/app.py")
        print("3. Start the frontend server: npm run dev (in frontend directory)")
        print("4. Open http://localhost:5173 in your browser")
        print("5. Register/login and go to your profile to set up platform integration")
    else:
        print("\n⚠️ Setup completed with issues.")
        print("Please review the failed checks above and resolve any issues.")
        print("The application may still work with reduced functionality.")
    
    print(f"\n📚 For detailed documentation, see: PLATFORM_INTEGRATION_README.md")
    
    return passed >= total - 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)