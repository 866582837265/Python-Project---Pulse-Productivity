# Quiz data for skill assessment
QUIZ_QUESTIONS = {
    "programming": [
        {
            "id": 1,
            "question": "What is the time complexity of binary search?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
            "correct": 1
        },
        {
            "id": 2,
            "question": "Which data structure uses LIFO principle?",
            "options": ["Queue", "Stack", "Array", "Linked List"],
            "correct": 1
        },
        {
            "id": 3,
            "question": "What is recursion?",
            "options": ["A loop", "A function calling itself", "An array", "A variable"],
            "correct": 1
        },
        {
            "id": 4,
            "question": "Which sorting algorithm has O(n log n) average time complexity?",
            "options": ["Bubble Sort", "Selection Sort", "Merge Sort", "Insertion Sort"],
            "correct": 2
        },
        {
            "id": 5,
            "question": "What does DFS stand for?",
            "options": ["Data File System", "Depth First Search", "Dynamic Function Set", "Direct File Storage"],
            "correct": 1
        }
    ]
}

ROADMAPS = {}

def get_domain_id(domain):
    return "programming"