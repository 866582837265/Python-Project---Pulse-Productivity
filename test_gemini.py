#!/usr/bin/env python3
import sys
sys.path.append('backend')
from ai.gemini_service import gemini_service

def test_gemini():
    print("Testing Gemini Service...")
    
    # Test question generation
    questions = gemini_service.generate_questions("Arrays", "Beginner", 3)
    
    print(f"Generated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q['question']}")
        for j, option in enumerate(q['options']):
            marker = "*" if j == q['answer'] else " "
            print(f"   {marker} {chr(65+j)}. {option}")
        print(f"   Explanation: {q['explanation']}")

if __name__ == "__main__":
    test_gemini()