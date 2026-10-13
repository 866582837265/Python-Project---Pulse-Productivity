import google.generativeai as genai
import json
import os
from datetime import datetime, timezone

class EnhancedGeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("[SUCCESS] Gemini AI configured")
        else:
            self.model = None
            print("[WARNING] GEMINI_API_KEY not found")

    def generate_topic_content(self, topic_name, difficulty="Beginner"):
        """Generate both coding and MCQ questions for a topic"""
        if not self.model:
            return self._generate_mock_content(topic_name, difficulty)
        
        try:
            java_template = "public class Main {\\n    public static void main(String[] args) {\\n        // Write your Java solution here\\n        System.out.println(\\\"Hello, Java!\\\");\\n    }\\n}"
            
            prompt = f"""
Generate comprehensive practice content for the Data Structures & Algorithms topic: "{topic_name}" at {difficulty} level.

IMPORTANT: All coding problems must use JAVA programming language only. Do not generate Python code.

Create exactly 5 coding problems and 5 multiple-choice questions.

Return ONLY a valid JSON object with this exact structure:
{{
    "coding_questions": [
        {{
            "id": "code_1",
            "title": "Problem Title",
            "description": "Clear problem description with constraints",
            "difficulty": "{difficulty}",
            "sample_input": "Example input",
            "sample_output": "Expected output",
            "hints": ["Hint 1", "Hint 2"],
            "starter_code": "{java_template}"
        }}
    ],
    "mcq_questions": [
        {{
            "id": "mcq_1",
            "question": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Why this answer is correct"
        }}
    ]
}}

Make problems practical and educational for {difficulty} level students learning {topic_name}.
All starter_code must be valid Java code with proper class structure and main method. Never generate Python code like 'def solution():' or 'pass' statements.
"""

            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean up response
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            data = json.loads(content)
            
            # Validate structure and ensure Java code
            if 'coding_questions' in data and 'mcq_questions' in data:
                # Check for Python code patterns and replace with Java
                for question in data['coding_questions']:
                    starter_code = question.get('starter_code', '')
                    if 'def solution' in starter_code or 'pass' in starter_code or starter_code.strip().startswith('def '):
                        print(f"⚠️ Detected Python code, replacing with Java template")
                        question['starter_code'] = "public class Main {\n    public static void main(String[] args) {\n        // Write your Java solution here\n        System.out.println(\"Hello, Java!\");\n    }\n}"
                
                print(f"✅ Generated {len(data['coding_questions'])} coding + {len(data['mcq_questions'])} MCQ questions for {topic_name}")
                return data
            else:
                print(f"❌ Invalid response structure for {topic_name}")
                return self._generate_mock_content(topic_name, difficulty)
                
        except Exception as e:
            print(f"❌ Gemini generation failed for {topic_name}: {e}")
            return self._generate_mock_content(topic_name, difficulty)

    def _generate_mock_content(self, topic_name, difficulty):
        """Generate mock content when Gemini is unavailable - Java only with 5+5 questions"""
        java_template = "public class Main {\n    public static void main(String[] args) {\n        // Write your Java solution here\n        System.out.println(\"Hello, Java!\");\n    }\n}"
        
        coding_questions = []
        mcq_questions = []
        
        # Generate 5 coding problems
        for i in range(1, 6):
            coding_questions.append({
                "id": f"code_{i}",
                "title": f"{topic_name} Problem {i}",
                "description": f"Solve a {difficulty.lower()} level {topic_name} problem using Java. This problem focuses on {topic_name} concepts and algorithms.",
                "difficulty": difficulty,
                "sample_input": f"Input: Example data {i}",
                "sample_output": f"Output: Expected result {i}",
                "hints": [f"Consider {topic_name} properties", f"Think about {difficulty.lower()} level approaches", "Use Java best practices"],
                "starter_code": java_template
            })
        
        # Generate 5 MCQ questions
        for i in range(1, 6):
            mcq_questions.append({
                "id": f"mcq_{i}",
                "question": f"Question {i}: What is an important concept in {topic_name}?",
                "options": [f"Correct answer for {topic_name}", f"Incorrect option A", f"Incorrect option B", f"Incorrect option C"],
                "correct_answer": 0,
                "explanation": f"This is a fundamental concept in {topic_name} that every developer should understand."
            })
        
        return {
            "coding_questions": coding_questions,
            "mcq_questions": mcq_questions
        }

# Global instance
enhanced_gemini_service = EnhancedGeminiService()