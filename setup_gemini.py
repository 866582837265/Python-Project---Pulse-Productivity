#!/usr/bin/env python3
"""
Setup script to configure Gemini API key for Pulse backend
"""

import os
import sys

def setup_gemini_api():
    print("🚀 Pulse Gemini API Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_path = os.path.join("backend", ".env")
    if not os.path.exists(env_path):
        print("❌ .env file not found in backend directory")
        print("Please make sure you're running this from the pulse root directory")
        return False
    
    # Read current .env content
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Check if Gemini API key is already configured
    if "GEMINI_API_KEY=" in env_content and not env_content.count("GEMINI_API_KEY=your-gemini-api-key-here"):
        print("✅ Gemini API key appears to be already configured")
        
        # Test if it's just commented out
        if "# GEMINI_API_KEY=" in env_content:
            print("⚠️  Gemini API key is commented out")
            uncomment = input("Would you like to uncomment it? (y/n): ").lower().strip()
            if uncomment == 'y':
                env_content = env_content.replace("# GEMINI_API_KEY=", "GEMINI_API_KEY=")
                with open(env_path, 'w') as f:
                    f.write(env_content)
                print("✅ Uncommented Gemini API key")
        return True
    
    print("\n📋 To get your Gemini API key:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated key")
    print()
    
    api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⏭️  Skipped API key setup")
        print("You can add it manually to backend/.env later:")
        print("GEMINI_API_KEY=your-api-key-here")
        return False
    
    # Add or update the API key in .env
    if "GEMINI_API_KEY=" in env_content:
        # Replace existing line
        lines = env_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("GEMINI_API_KEY=") or line.startswith("# GEMINI_API_KEY="):
                lines[i] = f"GEMINI_API_KEY={api_key}"
                break
        env_content = '\n'.join(lines)
    else:
        # Add new line
        env_content += f"\n\n# Gemini AI API Key\nGEMINI_API_KEY={api_key}\n"
    
    # Write updated .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ Gemini API key added to .env file")
    print("\n🔄 Next steps:")
    print("1. Restart your Flask server: python backend/app.py")
    print("2. Test the integration: python backend/test_fixes.py")
    print("3. Or visit: http://localhost:5000/api/test/gemini/Arrays")
    
    return True

def test_setup():
    """Test if the setup is working"""
    print("\n🧪 Testing setup...")
    
    try:
        import requests
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            
            # Test Gemini endpoint
            try:
                gemini_response = requests.get("http://localhost:5000/api/test/gemini/Arrays", timeout=10)
                data = gemini_response.json()
                
                if data.get("success"):
                    print("✅ Gemini integration test passed")
                    print(f"   - API Configured: {data.get('gemini_api_configured')}")
                    print(f"   - Questions Generated: {data.get('content_generated', {}).get('total_questions', 0)}")
                else:
                    print("⚠️  Gemini integration test failed")
                    print(f"   - Error: {data.get('error')}")
                    
            except Exception as e:
                print(f"⚠️  Could not test Gemini integration: {e}")
                
        else:
            print("❌ Backend server not responding properly")
            
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("Make sure Flask server is running: python backend/app.py")

if __name__ == "__main__":
    if setup_gemini_api():
        test_setup()
    
    print("\n📚 Documentation:")
    print("- Check FIXES_SUMMARY.md for detailed setup instructions")
    print("- Run 'python backend/test_fixes.py' for comprehensive testing")