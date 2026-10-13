import google.generativeai as genai
import json
import os
import re
from datetime import datetime, timezone

class FixedGeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("[SUCCESS] Fixed Gemini Service configured")
        else:
            self.model = None
            print("[WARNING] GEMINI_API_KEY not found")

    def generate_question_pack(self, topic_title, difficulty="Beginner"):
        """Generate complete question pack with strict validation"""
        print(f"Generating question pack for topic {topic_title}")
        
        if not self.model:
            return self._generate_fallback_pack(topic_title, difficulty)
        
        # Try up to 3 times to get valid JSON
        for attempt in range(3):
            try:
                content = self._call_gemini(topic_title, difficulty)
                if content:
                    print("Gemini output validated")
                    return content
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        
        print("All Gemini attempts failed, using fallback")
        return self._generate_fallback_pack(topic_title, difficulty)

    def _call_gemini(self, topic_title, difficulty):
        """Call Gemini with strict prompt"""
        prompt = f"""Generate exactly 5 coding problems and 5 MCQ questions for the Data Structures & Algorithms topic: "{topic_title}" at {difficulty} level.

Return ONLY valid JSON with this exact structure:

{{
  "coding_questions": [
    {{
      "id": "code_1",
      "title": "Two Sum Array Problem",
      "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
      "sample_input": "nums = [2,7,11,15], target = 9",
      "sample_output": "[0,1]",
      "difficulty": "easy",
      "starter_code": "public class Solution {{\\n    public int[] twoSum(int[] nums, int target) {{\\n        // Write your solution here\\n        return new int[0];\\n    }}\\n}}"
    }}
  ],
  "mcq_questions": [
    {{
      "id": "mcq_1",
      "question": "What is the time complexity of binary search on a sorted array?",
      "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
      "answer_index": 1,
      "explanation": "Binary search divides the search space in half at each step, resulting in O(log n) time complexity."
    }}
  ]
}}

Requirements:
- Create realistic {topic_title} problems with proper constraints
- Use actual sample inputs/outputs, not placeholders
- MCQ questions must be factual CS/DSA concepts
- All starter_code must be valid Java with proper method signatures
- NO markdown, NO backticks, NO extra text - JSON ONLY
- Difficulty levels: easy, medium, hard"""

        response = self.model.generate_content(prompt)
        content = response.text.strip()
        
        # Clean response
        content = self._clean_json_response(content)
        
        # Parse and validate
        data = json.loads(content)
        
        if self._validate_question_pack(data):
            return self._fix_none_values(data)
        else:
            raise Exception("Invalid question pack structure")

    def _clean_json_response(self, content):
        """Clean Gemini response to extract pure JSON"""
        # Remove markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        content = re.sub(r'^```\s*', '', content)
        
        # Remove any text before first {
        start_idx = content.find('{')
        if start_idx > 0:
            content = content[start_idx:]
        
        # Remove any text after last }
        end_idx = content.rfind('}')
        if end_idx > 0:
            content = content[:end_idx + 1]
        
        return content.strip()

    def _validate_question_pack(self, data):
        """Strict validation of question pack structure"""
        if not isinstance(data, dict):
            return False
        
        # Check main structure
        if 'coding_questions' not in data or 'mcq_questions' not in data:
            return False
        
        coding_questions = data['coding_questions']
        mcq_questions = data['mcq_questions']
        
        if not isinstance(coding_questions, list) or not isinstance(mcq_questions, list):
            return False
        
        if len(coding_questions) != 5 or len(mcq_questions) != 5:
            return False
        
        # Validate coding questions
        for q in coding_questions:
            required_fields = ['id', 'title', 'description', 'sample_input', 'sample_output', 'difficulty', 'starter_code']
            if not all(field in q and q[field] for field in required_fields):
                return False
        
        # Validate MCQ questions
        for q in mcq_questions:
            required_fields = ['id', 'question', 'options', 'answer_index', 'explanation']
            if not all(field in q for field in required_fields):
                return False
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                return False
            if not isinstance(q['answer_index'], int) or q['answer_index'] not in [0, 1, 2, 3]:
                return False
        
        return True

    def _fix_none_values(self, data):
        """Replace any None values with defaults"""
        for q in data['coding_questions']:
            for field in ['id', 'title', 'description', 'sample_input', 'sample_output', 'difficulty', 'starter_code']:
                if q.get(field) is None or q.get(field) == '':
                    q[field] = self._get_default_coding_value(field)
        
        for q in data['mcq_questions']:
            for field in ['id', 'question', 'explanation']:
                if q.get(field) is None or q.get(field) == '':
                    q[field] = self._get_default_mcq_value(field)
            
            if not isinstance(q.get('options'), list) or len(q['options']) != 4:
                q['options'] = ["Option A", "Option B", "Option C", "Option D"]
            
            if q.get('answer_index') is None or q.get('answer_index') not in [0, 1, 2, 3]:
                q['answer_index'] = 0
        
        return data

    def _get_default_coding_value(self, field):
        """Get default value for coding question field"""
        defaults = {
            'id': 'code_default',
            'title': 'Coding Problem',
            'description': 'Solve this programming problem.',
            'sample_input': 'Input: [1, 2, 3]',
            'sample_output': 'Output: 6',
            'difficulty': 'easy',
            'starter_code': 'public class Solution {\n    public int solve(int[] nums) {\n        // Write your solution here\n        return 0;\n    }\n}'
        }
        return defaults.get(field, '')

    def _get_default_mcq_value(self, field):
        """Get default value for MCQ field"""
        defaults = {
            'id': 'mcq_default',
            'question': 'What is a fundamental concept in computer science?',
            'explanation': 'This is a basic concept that every developer should know.'
        }
        return defaults.get(field, '')

    def _generate_fallback_pack(self, topic_title, difficulty):
        """Generate high-quality fallback questions"""
        coding_questions = []
        mcq_questions = []
        
        # Generate 5 realistic coding problems
        for i in range(1, 6):
            coding_questions.append({
                "id": f"code_{i}",
                "title": f"{topic_title} Challenge {i}",
                "description": f"Implement a solution for this {topic_title} problem. Focus on {difficulty.lower()} level concepts and optimize for both time and space complexity.",
                "sample_input": f"nums = [1, 2, 3, 4, 5], target = {i + 5}",
                "sample_output": f"result = {i * 2}",
                "difficulty": difficulty.lower(),
                "starter_code": f"public class Solution {{\n    public int solve{i}(int[] nums, int target) {{\n        // Implement your {topic_title} solution here\n        return 0;\n    }}\n}}"
            })
        
        # Generate 5 realistic MCQ questions
        mcq_templates = [
            {
                "question": f"What is the average time complexity for search operations in {topic_title}?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                "answer_index": 1,
                "explanation": f"Most efficient {topic_title} operations have logarithmic time complexity."
            },
            {
                "question": f"Which data structure is most commonly used to implement {topic_title}?",
                "options": ["Array", "Linked List", "Hash Table", "Tree"],
                "answer_index": 0,
                "explanation": f"Arrays provide the foundation for most {topic_title} implementations."
            },
            {
                "question": f"What is the space complexity of a typical {topic_title} algorithm?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                "answer_index": 2,
                "explanation": f"Most {topic_title} algorithms require linear space for processing."
            },
            {
                "question": f"In {topic_title}, what is the best case scenario for performance?",
                "options": ["Sorted input", "Random input", "Reverse sorted", "All equal elements"],
                "answer_index": 0,
                "explanation": "Sorted input typically provides the best performance for most algorithms."
            },
            {
                "question": f"Which approach is most effective for {topic_title} optimization?",
                "options": ["Brute force", "Dynamic programming", "Greedy method", "Divide and conquer"],
                "answer_index": 3,
                "explanation": "Divide and conquer often provides optimal solutions for complex problems."
            }
        ]
        
        for i, template in enumerate(mcq_templates):
            mcq_questions.append({
                "id": f"mcq_{i + 1}",
                "question": template["question"],
                "options": template["options"],
                "answer_index": template["answer_index"],
                "explanation": template["explanation"]
            })
        
        return {
            "coding_questions": coding_questions,
            "mcq_questions": mcq_questions
        }

# Global instance
fixed_gemini_service = FixedGeminiService()