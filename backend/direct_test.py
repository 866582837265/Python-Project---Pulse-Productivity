#!/usr/bin/env python3
"""
Direct test of the enhanced_gemini_service
"""

try:
    from ai.enhanced_gemini_service import enhanced_gemini_service
    print("Enhanced Gemini Service imported successfully")
    
    # Test content generation
    content = enhanced_gemini_service.generate_topic_content("Arrays", "Beginner")
    
    if content and 'coding_questions' in content:
        for i, question in enumerate(content['coding_questions']):
            starter_code = question.get('starter_code', '')
            print(f"\nQuestion {i+1} starter code:")
            print(starter_code)
            print("-" * 50)
            
            # Check if it's Java or Python
            if "public class Main" in starter_code:
                print("RESULT: Java template detected!")
            elif "def solution" in starter_code or "pass" in starter_code:
                print("RESULT: Python template detected!")
            else:
                print("RESULT: Unknown template format")
    else:
        print("No coding questions generated")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Testing mock service instead...")
    
    # Test the mock service
    class MockEnhancedGeminiService:
        def generate_topic_content(self, topic_name, difficulty):
            return {
                "coding_questions": [{
                    "id": "code_1",
                    "title": f"Basic {topic_name} Problem",
                    "description": f"Solve a fundamental {topic_name} problem using Java.",
                    "difficulty": difficulty,
                    "sample_input": "Input: [1, 2, 3]",
                    "sample_output": "Output: 6",
                    "hints": [f"Think about {topic_name} properties"],
                    "starter_code": "public class Main {\n    public static void main(String[] args) {\n        // Write your Java solution here\n        System.out.println(\"Hello, Java!\");\n    }\n}"
                }],
                "mcq_questions": [{
                    "id": "mcq_1",
                    "question": f"What is a key concept in {topic_name}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0,
                    "explanation": f"This is fundamental to {topic_name}."
                }]
            }
    
    mock_service = MockEnhancedGeminiService()
    content = mock_service.generate_topic_content("Arrays", "Beginner")
    
    if content and 'coding_questions' in content:
        starter_code = content['coding_questions'][0].get('starter_code', '')
        print(f"\nMock service starter code:")
        print(starter_code)
        
        if "public class Main" in starter_code:
            print("RESULT: Java template detected in mock!")
        elif "def solution" in starter_code:
            print("RESULT: Python template detected in mock!")
        else:
            print("RESULT: Unknown template format in mock")