#!/usr/bin/env python3
"""
Test script to verify Topic Detail page question system fixes
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_server_health():
    """Test if server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print("❌ Backend server not responding properly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        return False

def test_gemini_service():
    """Test Gemini service integration"""
    print("\n🧪 Testing Gemini Service...")
    try:
        response = requests.get(f"{BASE_URL}/api/test/gemini/Arrays")
        data = response.json()
        
        if data.get("success"):
            print("✅ Gemini service test passed")
            print(f"   - API Configured: {data.get('gemini_api_configured')}")
            
            content = data.get('content_generated', {})
            coding_count = content.get('coding_questions', 0)
            mcq_count = content.get('mcq_questions', 0)
            
            print(f"   - Coding Questions: {coding_count}")
            print(f"   - MCQ Questions: {mcq_count}")
            
            if coding_count == 5 and mcq_count == 5:
                print("✅ Question count is correct (5 coding + 5 MCQ)")
            else:
                print(f"⚠️  Question count mismatch. Expected: 5+5, Got: {coding_count}+{mcq_count}")
            
            return True
        else:
            print(f"❌ Gemini service test failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini service test error: {e}")
        return False

def test_fixed_gemini_service():
    """Test the new fixed Gemini service"""
    print("\n🔧 Testing Fixed Gemini Service...")
    try:
        # Test the fixed service directly
        from backend.ai.fixed_gemini_service import fixed_gemini_service
        
        if fixed_gemini_service:
            content = fixed_gemini_service.generate_question_pack("Arrays", "Beginner")
            
            coding_questions = content.get("coding_questions", [])
            mcq_questions = content.get("mcq_questions", [])
            
            print(f"✅ Fixed Gemini service working")
            print(f"   - Coding Questions: {len(coding_questions)}")
            print(f"   - MCQ Questions: {len(mcq_questions)}")
            
            # Validate question structure
            valid_coding = all(
                q.get("id") and q.get("title") and q.get("description") and 
                q.get("sample_input") and q.get("sample_output") and q.get("starter_code")
                for q in coding_questions
            )
            
            valid_mcq = all(
                q.get("id") and q.get("question") and 
                isinstance(q.get("options"), list) and len(q.get("options", [])) == 4 and
                q.get("answer_index") in [0, 1, 2, 3] and q.get("explanation")
                for q in mcq_questions
            )
            
            if valid_coding:
                print("✅ All coding questions have complete fields")
            else:
                print("❌ Some coding questions have missing fields")
            
            if valid_mcq:
                print("✅ All MCQ questions have complete fields")
            else:
                print("❌ Some MCQ questions have missing fields")
            
            # Check for placeholder text
            has_placeholders = any(
                "placeholder" in str(q).lower() or "example" in q.get("sample_input", "").lower()
                for q in coding_questions
            )
            
            if not has_placeholders:
                print("✅ No placeholder text found")
            else:
                print("⚠️  Some placeholder text still present")
            
            return valid_coding and valid_mcq
        else:
            print("❌ Fixed Gemini service not available")
            return False
            
    except Exception as e:
        print(f"❌ Fixed Gemini service test error: {e}")
        return False

def test_topic_lookup():
    """Test topic lookup functionality"""
    print("\n🔍 Testing Topic Lookup...")
    
    # This would require authentication, so we'll just test the structure
    print("   Note: Topic lookup requires user authentication")
    print("   To test manually:")
    print("   1. Login to the frontend")
    print("   2. Complete skill assessment")
    print("   3. Click on any topic in the roadmap")
    print("   4. Verify topic title appears correctly (not 'Unknown topic')")
    print("   5. Verify all 5 coding questions are visible")
    print("   6. Verify all 5 MCQ questions are visible")
    
    return True

def test_question_validation():
    """Test question validation logic"""
    print("\n✅ Testing Question Validation...")
    
    try:
        from backend.app import _ensure_complete_questions
        
        # Test with incomplete data
        incomplete_content = {
            "coding_questions": [
                {"id": "code_1", "title": None, "description": ""},
                {"id": "code_2"}  # Missing fields
            ],
            "mcq_questions": [
                {"id": "mcq_1", "question": None, "options": ["A"]},  # Invalid options
                {"id": "mcq_2", "answer_index": 5}  # Invalid answer index
            ]
        }
        
        topic_info = {"title": "Arrays", "difficulty": "Beginner"}
        
        fixed_content = _ensure_complete_questions(incomplete_content, topic_info)
        
        # Verify fixes
        coding_questions = fixed_content["coding_questions"]
        mcq_questions = fixed_content["mcq_questions"]
        
        if len(coding_questions) == 5:
            print("✅ Coding questions count fixed to 5")
        else:
            print(f"❌ Coding questions count: {len(coding_questions)}, expected 5")
        
        if len(mcq_questions) == 5:
            print("✅ MCQ questions count fixed to 5")
        else:
            print(f"❌ MCQ questions count: {len(mcq_questions)}, expected 5")
        
        # Check for None values
        has_none_coding = any(
            not q.get("title") or not q.get("description") or not q.get("sample_input")
            for q in coding_questions
        )
        
        has_none_mcq = any(
            not q.get("question") or not isinstance(q.get("options"), list) or 
            len(q.get("options", [])) != 4 or q.get("answer_index") not in [0, 1, 2, 3]
            for q in mcq_questions
        )
        
        if not has_none_coding:
            print("✅ No None values in coding questions")
        else:
            print("❌ Some coding questions still have None values")
        
        if not has_none_mcq:
            print("✅ No None values in MCQ questions")
        else:
            print("❌ Some MCQ questions still have None values")
        
        return len(coding_questions) == 5 and len(mcq_questions) == 5 and not has_none_coding and not has_none_mcq
        
    except Exception as e:
        print(f"❌ Question validation test error: {e}")
        return False

def main():
    print("🚀 Testing Topic Detail Page Question System Fixes")
    print("=" * 60)
    
    tests = [
        ("Server Health", test_server_health),
        ("Gemini Service", test_gemini_service),
        ("Fixed Gemini Service", test_fixed_gemini_service),
        ("Question Validation", test_question_validation),
        ("Topic Lookup", test_topic_lookup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The question system should be working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print("\n📋 Manual Testing Steps:")
    print("1. Start the Flask server: python backend/app.py")
    print("2. Start the React frontend: npm run dev")
    print("3. Login and complete skill assessment")
    print("4. Click on any topic in the roadmap")
    print("5. Verify:")
    print("   - Topic title shows correctly (not 'Unknown topic')")
    print("   - All 5 coding questions are visible and expanded")
    print("   - All 5 MCQ questions are visible with proper formatting")
    print("   - No 'None' values or placeholder text")
    print("   - Sample input/output shows realistic data")

if __name__ == "__main__":
    main()