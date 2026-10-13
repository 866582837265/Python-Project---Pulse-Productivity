import os
import json
import uuid
import google.generativeai as genai
from typing import List, Dict, Any

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            print("[WARNING] GEMINI_API_KEY not found, using fallback questions")
            self.model = None

    def generate_questions(self, topic: str, difficulty: str, count: int = 10) -> List[Dict[str, Any]]:
        """Generate coding questions for a specific topic using Gemini AI"""
        
        if not self.model:
            return self._get_fallback_questions(topic, difficulty, count)
        
        try:
            prompt = f"""
Generate {count} multiple choice questions for the topic "{topic}" at {difficulty} level.
Each question should test practical coding knowledge and problem-solving skills.

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "id": "unique_id",
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": 0,
    "explanation": "Brief explanation of the correct answer"
  }}
]

Requirements:
- Questions should be practical and test real coding scenarios
- Options should be plausible and well-formatted
- Answer should be the index (0-3) of the correct option
- Include brief explanations
- Focus on {difficulty} level concepts for {topic}
"""

            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            questions = json.loads(response_text)
            
            # Validate and add unique IDs
            validated_questions = []
            for i, q in enumerate(questions[:count]):
                if self._validate_question(q):
                    q["id"] = str(uuid.uuid4())
                    validated_questions.append(q)
            
            if len(validated_questions) >= 5:  # At least 5 valid questions
                print(f"✨ Gemini generated {len(validated_questions)} questions for {topic}")
                return validated_questions
            else:
                print(f"❌ Gemini generated insufficient valid questions, using fallback")
                return self._get_fallback_questions(topic, difficulty, count)
                
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self._get_fallback_questions(topic, difficulty, count)

    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate question structure"""
        required_fields = ["question", "options", "answer"]
        
        if not all(field in question for field in required_fields):
            return False
        
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            return False
        
        if not isinstance(question["answer"], int) or question["answer"] not in [0, 1, 2, 3]:
            return False
        
        return True

    def _get_fallback_questions(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Fallback questions when Gemini API is unavailable"""
        
        fallback_questions = {
            "Arrays Basics": [
                {
                    "id": str(uuid.uuid4()),
                    "question": "What is the time complexity of accessing an element in an array by index?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "answer": 0,
                    "explanation": "Array elements can be accessed directly using their index in constant time."
                },
                {
                    "id": str(uuid.uuid4()),
                    "question": "Which operation is most efficient on a dynamic array?",
                    "options": ["Insertion at beginning", "Insertion at end", "Deletion from middle", "Search for element"],
                    "answer": 1,
                    "explanation": "Insertion at the end of a dynamic array is typically O(1) amortized."
                }
            ],
            "String Manipulation": [
                {
                    "id": str(uuid.uuid4()),
                    "question": "What is the time complexity of string concatenation in most languages?",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "answer": 2,
                    "explanation": "String concatenation typically requires copying both strings, making it O(n)."
                }
            ],
            "Binary Trees": [
                {
                    "id": str(uuid.uuid4()),
                    "question": "What is the maximum number of nodes at level k in a binary tree?",
                    "options": ["k", "2k", "2^k", "2^(k-1)"],
                    "answer": 2,
                    "explanation": "At level k, a binary tree can have at most 2^k nodes."
                }
            ]
        }
        
        # Get questions for the topic or use generic ones
        questions = fallback_questions.get(topic, fallback_questions["Arrays Basics"])
        
        # Extend with generic questions if needed
        while len(questions) < count:
            generic_q = {
                "id": str(uuid.uuid4()),
                "question": f"What is a key concept in {topic}?",
                "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
                "answer": 0,
                "explanation": f"This is a fundamental concept in {topic}."
            }
            questions.append(generic_q)
        
        return questions[:count]

# Global instance
gemini_service = GeminiService()