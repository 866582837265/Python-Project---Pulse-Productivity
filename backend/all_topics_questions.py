# Complete Questions Database for All DSA Topics

ALL_TOPICS_QUESTIONS = {
    "Arrays Basics": {
        "mcqs": [
            {"question": "What is the index of the first element in an array?", "options": ["0", "1", "-1", "Depends on the programming language"], "correct_answer": "0"},
            {"question": "What is the time complexity of accessing an element by index in an array?", "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"], "correct_answer": "O(1)"},
            {"question": "Which of the following correctly declares an array in Java?", "options": ["int arr = new int[5];", "int arr[] = new int[5];", "int arr() = new int[5];", "array arr = int[5];"], "correct_answer": "int arr[] = new int[5];"},
            {"question": "Which of these operations is not efficient in arrays?", "options": ["Accessing an element", "Updating an element", "Inserting at the beginning", "Traversing the array"], "correct_answer": "Inserting at the beginning"},
            {"question": "What happens if you try to access an array index out of bounds?", "options": ["Returns 0", "Program crashes / throws exception", "Returns garbage value", "Automatically resizes the array"], "correct_answer": "Program crashes / throws exception"}
        ],
        "coding_questions": [
            {"title": "Find the Sum of All Elements in an Array", "problem_statement": "Calculate the sum of all elements in the given array.", "input_format": "[1, 2, 3, 4]", "output_format": "10"},
            {"title": "Find the Maximum Element in an Array", "problem_statement": "Find the largest element in the given array.", "input_format": "[5, 12, 3]", "output_format": "12"},
            {"title": "Count How Many Even Numbers Are in an Array", "problem_statement": "Count the number of even numbers in the array.", "input_format": "[1, 2, 4, 5, 8]", "output_format": "3"},
            {"title": "Reverse the Array (Without Using Built-In Reverse)", "problem_statement": "Reverse the array without using built-in reverse function.", "input_format": "[10, 20, 30]", "output_format": "[30, 20, 10]"},
            {"title": "Check if an Element Exists in an Array", "problem_statement": "Check if a target element exists in the array.", "input_format": "Array: [7, 9, 2], Target: 9", "output_format": "true"}
        ]
    },
    
    "String Manipulation": {
        "mcqs": [
            {"question": "What is a string?", "options": ["A number", "A sequence of characters", "A boolean value", "An array of integers"], "correct_answer": "A sequence of characters"},
            {"question": "Which method returns the length of a string?", "options": ["size()", "length()", "count()", "len()"], "correct_answer": "length()"},
            {"question": "What is a palindrome?", "options": ["A string with only vowels", "A string that reads same forwards and backwards", "A string with numbers", "An empty string"], "correct_answer": "A string that reads same forwards and backwards"},
            {"question": "String concatenation means:", "options": ["Splitting strings", "Joining strings together", "Reversing strings", "Counting characters"], "correct_answer": "Joining strings together"},
            {"question": "Which characters are vowels?", "options": ["a, e, i, o, u", "b, c, d, f, g", "x, y, z", "All letters"], "correct_answer": "a, e, i, o, u"}
        ],
        "coding_questions": [
            {"title": "Count Vowels", "problem_statement": "Count the number of vowels (a, e, i, o, u) in a given string.", "input_format": "A string", "output_format": "Single integer (vowel count)"},
            {"title": "Reverse String", "problem_statement": "Reverse the given string.", "input_format": "A string", "output_format": "Reversed string"},
            {"title": "Check Palindrome", "problem_statement": "Check if the given string is a palindrome (reads same forwards and backwards).", "input_format": "A string", "output_format": "Boolean (true/false)"},
            {"title": "Remove Spaces", "problem_statement": "Remove all spaces from the given string.", "input_format": "A string with spaces", "output_format": "String without spaces"},
            {"title": "Count Characters", "problem_statement": "Count how many times a specific character appears in the string.", "input_format": "A string and a character", "output_format": "Single integer (character count)"}
        ]
    },

    "Basic Loops": {
        "mcqs": [
            {"question": "What is the purpose of a loop?", "options": ["To store data", "To repeat code multiple times", "To make decisions", "To define functions"], "correct_answer": "To repeat code multiple times"},
            {"question": "Which loop runs for a fixed number of times?", "options": ["while loop", "for loop", "do-while loop", "infinite loop"], "correct_answer": "for loop"},
            {"question": "When does a while loop stop?", "options": ["When condition becomes true", "When condition becomes false", "After 10 iterations", "Never"], "correct_answer": "When condition becomes false"},
            {"question": "What is an infinite loop?", "options": ["A loop that runs very fast", "A loop that never stops", "A loop with no code", "A loop that runs once"], "correct_answer": "A loop that never stops"},
            {"question": "Loop iteration means:", "options": ["Starting the loop", "One complete execution of loop body", "Ending the loop", "Skipping the loop"], "correct_answer": "One complete execution of loop body"}
        ],
        "coding_questions": [
            {"title": "Print Numbers 1 to N", "problem_statement": "Print all numbers from 1 to N using a loop.", "input_format": "Single integer N", "output_format": "Numbers from 1 to N, each on new line"},
            {"title": "Sum of First N Numbers", "problem_statement": "Calculate the sum of first N natural numbers using a loop.", "input_format": "Single integer N", "output_format": "Single integer (sum)"},
            {"title": "Count Digits", "problem_statement": "Count the number of digits in a given number using a loop.", "input_format": "Single integer", "output_format": "Single integer (digit count)"},
            {"title": "Print Even Numbers", "problem_statement": "Print all even numbers from 1 to N using a loop.", "input_format": "Single integer N", "output_format": "Even numbers from 1 to N"},
            {"title": "Factorial Calculation", "problem_statement": "Calculate the factorial of a number using a loop.", "input_format": "Single integer N", "output_format": "Single integer (factorial)"}
        ]
    }
}

def get_topic_questions_complete(topic_name):
    """Get questions for any topic"""
    return ALL_TOPICS_QUESTIONS.get(topic_name, {"mcqs": [], "coding_questions": []})