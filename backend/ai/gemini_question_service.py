import google.generativeai as genai
import json
import os
from datetime import datetime, timezone

class GeminiQuestionService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("[SUCCESS] Gemini Question Service configured")
        else:
            self.model = None
            print("[WARNING] GEMINI_API_KEY not found")

    def generate_question_pack(self, topic_title, difficulty, count_coding=5, count_mcq=5):
        """Generate question pack with specified counts"""
        if not self.model:
            return self._generate_fallback_pack(topic_title, difficulty, count_coding, count_mcq)
        
        try:
            prompt = f"""
Generate a comprehensive question pack for the Data Structures & Algorithms topic: "{topic_title}" at {difficulty} level.

Create exactly {count_coding} coding problems and {count_mcq} multiple-choice questions.

Return ONLY valid JSON with this exact structure:
{{
    "coding_questions": [
        {{
            "id": "code_1",
            "title": "Problem Title",
            "description": "Clear problem description with constraints and requirements",
            "difficulty": "{difficulty}",
            "sample_input": "Example input format",
            "sample_output": "Expected output format",
            "starter_code": "public class Main {{\\n    public static void main(String[] args) {{\\n        // Write your Java solution here\\n    }}\\n}}"
        }}
    ],
    "mcq_questions": [
        {{
            "id": "mcq_1",
            "question": "Question text about {topic_title}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Detailed explanation of why this answer is correct"
        }}
    ]
}}

Requirements:
- All coding problems must use Java programming language only
- Make problems practical and educational for {difficulty} level
- Ensure starter_code is valid Java with proper class structure
- MCQ questions should test conceptual understanding of {topic_title}
- Options should be plausible and well-formatted
- Explanations should be clear and educational
"""

            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean JSON response
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            
            # Validate structure
            if self._validate_question_pack(data, count_coding, count_mcq):
                print(f"✅ Generated {len(data['coding_questions'])} coding + {len(data['mcq_questions'])} MCQ questions for {topic_title}")
                return data
            else:
                print(f"❌ Invalid Gemini response structure for {topic_title}")
                return self._generate_fallback_pack(topic_title, difficulty, count_coding, count_mcq)
                
        except Exception as e:
            print(f"❌ Gemini generation failed for {topic_title}: {e}")
            return self._generate_fallback_pack(topic_title, difficulty, count_coding, count_mcq)

    def _validate_question_pack(self, data, expected_coding, expected_mcq):
        """Validate question pack structure"""
        if not isinstance(data, dict):
            return False
        
        coding_questions = data.get('coding_questions', [])
        mcq_questions = data.get('mcq_questions', [])
        
        if len(coding_questions) < expected_coding or len(mcq_questions) < expected_mcq:
            return False
        
        # Validate coding questions
        for q in coding_questions:
            required_fields = ['id', 'title', 'description', 'difficulty', 'sample_input', 'sample_output', 'starter_code']
            if not all(field in q for field in required_fields):
                return False
        
        # Validate MCQ questions
        for q in mcq_questions:
            required_fields = ['id', 'question', 'options', 'correct_answer', 'explanation']
            if not all(field in q for field in required_fields):
                return False
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                return False
            if not isinstance(q['correct_answer'], int) or q['correct_answer'] not in [0, 1, 2, 3]:
                return False
        
        return True

    def _generate_fallback_pack(self, topic_title, difficulty, count_coding, count_mcq):
        """Generate fallback questions when Gemini is unavailable"""
        java_template = "public class Main {\n    public static void main(String[] args) {\n        // Write your Java solution here\n        System.out.println(\"Hello, Java!\");\n    }\n}"
        
        coding_questions = []
        mcq_questions = []
        
        # Generate coding problems
        for i in range(1, count_coding + 1):
            coding_questions.append({
                "id": f"code_{i}",
                "title": f"{topic_title} Problem {i}",
                "description": f"Solve a {difficulty.lower()} level {topic_title} problem using Java. This problem focuses on {topic_title} concepts and algorithms.",
                "difficulty": difficulty,
                "sample_input": f"Input: Example data {i}",
                "sample_output": f"Output: Expected result {i}",
                "starter_code": java_template
            })
        
        # Generate MCQ questions
        for i in range(1, count_mcq + 1):
            mcq_questions.append({
                "id": f"mcq_{i}",
                "question": f"Question {i}: What is an important concept in {topic_title}?",
                "options": [f"Correct answer for {topic_title}", f"Incorrect option A", f"Incorrect option B", f"Incorrect option C"],
                "correct_answer": 0,
                "explanation": f"This is a fundamental concept in {topic_title} that every developer should understand."
            })
        
        return {
            "coding_questions": coding_questions,
            "mcq_questions": mcq_questions
        }

# Global instance
gemini_question_service = GeminiQuestionService()