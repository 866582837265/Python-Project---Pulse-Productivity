# Topic Questions Database - MCQs and Coding Questions for each roadmap topic

TOPIC_QUESTIONS = {
    "arrays": {
        "mcq_questions": [
            {
                "id": "arrays_mcq_1",
                "question": "Which of the following best describes an array?",
                "options": ["A group of unrelated values", "A list of items stored in continuous memory", "A file containing numbers", "A random collection of data"],
                "answer_index": 1,
                "explanation": "Arrays store elements in continuous memory locations, allowing fast access by index."
            },
            {
                "id": "arrays_mcq_2", 
                "question": "Array indexing starts from:",
                "options": ["-1", "0", "1", "Depends on language"],
                "answer_index": 1,
                "explanation": "In most programming languages, array indexing starts from 0."
            },
            {
                "id": "arrays_mcq_3",
                "question": "Accessing an element in an array by index takes:",
                "options": ["Constant time", "Logarithmic time", "Linear time", "Complex time"],
                "answer_index": 0,
                "explanation": "Array access by index is O(1) - constant time operation."
            },
            {
                "id": "arrays_mcq_4",
                "question": "Which operation is fastest in arrays?",
                "options": ["Insert at beginning", "Delete middle element", "Access using index", "Reverse array"],
                "answer_index": 2,
                "explanation": "Random access by index is the fastest operation in arrays."
            },
            {
                "id": "arrays_mcq_5",
                "question": "Which structure stores elements of the same type?",
                "options": ["Stack", "Array", "Queue", "Tree"],
                "answer_index": 1,
                "explanation": "Arrays typically store elements of the same data type."
            }
        ],
        "coding_questions": [
            {
                "id": "arrays_code_1",
                "title": "Find Largest Element",
                "description": "Find the largest element in an array of integers.",
                "sample_input": "arr = [3, 7, 1, 9, 2]",
                "sample_output": "9",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int findLargest(int[] arr) {\n        // Write your solution here\n        return 0;\n    }\n}"
            },
            {
                "id": "arrays_code_2",
                "title": "Count Occurrences",
                "description": "Count how many times a given number appears in an array.",
                "sample_input": "arr = [1, 2, 3, 2, 2, 4], target = 2",
                "sample_output": "3",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int countOccurrences(int[] arr, int target) {\n        // Write your solution here\n        return 0;\n    }\n}"
            },
            {
                "id": "arrays_code_3",
                "title": "Reverse Array",
                "description": "Print all elements of an array in reverse order.",
                "sample_input": "arr = [1, 2, 3, 4, 5]",
                "sample_output": "[5, 4, 3, 2, 1]",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public void printReverse(int[] arr) {\n        // Write your solution here\n    }\n}"
            },
            {
                "id": "arrays_code_4",
                "title": "Array Sum",
                "description": "Find the sum of all elements in an array.",
                "sample_input": "arr = [1, 2, 3, 4, 5]",
                "sample_output": "15",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int arraySum(int[] arr) {\n        // Write your solution here\n        return 0;\n    }\n}"
            },
            {
                "id": "arrays_code_5",
                "title": "Second Largest",
                "description": "Find the second largest number in an array.",
                "sample_input": "arr = [3, 7, 1, 9, 2]",
                "sample_output": "7",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int secondLargest(int[] arr) {\n        // Write your solution here\n        return 0;\n    }\n}"
            }
        ]
    },
    
    "strings": {
        "mcq_questions": [
            {
                "id": "strings_mcq_1",
                "question": "A string is a sequence of:",
                "options": ["Numbers", "Characters", "Functions", "Variables"],
                "answer_index": 1,
                "explanation": "Strings are sequences of characters."
            },
            {
                "id": "strings_mcq_2",
                "question": "Which operation gives string length?",
                "options": ["size()", "count()", "length()", "range()"],
                "answer_index": 2,
                "explanation": "The length() method returns the number of characters in a string."
            },
            {
                "id": "strings_mcq_3",
                "question": "'racecar' is special because it is a:",
                "options": ["Loop", "Palindrome", "Array", "Pattern"],
                "answer_index": 1,
                "explanation": "A palindrome reads the same forwards and backwards."
            },
            {
                "id": "strings_mcq_4",
                "question": "Joining strings together is called:",
                "options": ["Combining", "Rewriting", "Concatenation", "Mapping"],
                "answer_index": 2,
                "explanation": "String concatenation is the process of joining strings together."
            },
            {
                "id": "strings_mcq_5",
                "question": "Which structure is used to store words?",
                "options": ["Array", "String", "Queue", "Graph"],
                "answer_index": 1,
                "explanation": "Strings are used to store sequences of characters, including words."
            }
        ],
        "coding_questions": [
            {
                "id": "strings_code_1",
                "title": "Count Vowels",
                "description": "Count the number of vowels in a string.",
                "sample_input": "str = 'hello world'",
                "sample_output": "3",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int countVowels(String str) {\n        // Write your solution here\n        return 0;\n    }\n}"
            },
            {
                "id": "strings_code_2",
                "title": "Remove Spaces",
                "description": "Remove all spaces from a string.",
                "sample_input": "str = 'hello world'",
                "sample_output": "'helloworld'",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public String removeSpaces(String str) {\n        // Write your solution here\n        return \"\";\n    }\n}"
            },
            {
                "id": "strings_code_3",
                "title": "Check Palindrome",
                "description": "Check if a string is a palindrome.",
                "sample_input": "str = 'racecar'",
                "sample_output": "true",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public boolean isPalindrome(String str) {\n        // Write your solution here\n        return false;\n    }\n}"
            },
            {
                "id": "strings_code_4",
                "title": "First Non-Repeating Character",
                "description": "Find the first non-repeating character in a string.",
                "sample_input": "str = 'abccba'",
                "sample_output": "'No non-repeating character'",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public char firstNonRepeating(String str) {\n        // Write your solution here\n        return ' ';\n    }\n}"
            },
            {
                "id": "strings_code_5",
                "title": "Reverse String",
                "description": "Reverse a string without using built-in functions.",
                "sample_input": "str = 'hello'",
                "sample_output": "'olleh'",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public String reverseString(String str) {\n        // Write your solution here\n        return \"\";\n    }\n}"
            }
        ]
    },

    "loops": {
        "mcq_questions": [
            {
                "id": "loops_mcq_1",
                "question": "A loop helps in:",
                "options": ["Repeating tasks", "Stopping code", "Storing data", "Sorting files"],
                "answer_index": 0,
                "explanation": "Loops are used to repeat a block of code multiple times."
            },
            {
                "id": "loops_mcq_2",
                "question": "Which loop runs a fixed number of times?",
                "options": ["while", "do-while", "for", "repeat"],
                "answer_index": 2,
                "explanation": "For loops typically run for a predetermined number of iterations."
            },
            {
                "id": "loops_mcq_3",
                "question": "A loop stops when:",
                "options": ["The condition becomes false", "It feels tired", "Code ends", "User presses a key"],
                "answer_index": 0,
                "explanation": "Loops continue while their condition is true and stop when it becomes false."
            },
            {
                "id": "loops_mcq_4",
                "question": "Infinite loops happen when:",
                "options": ["Condition never becomes false", "No elements exist", "Loop gets skipped", "Code is correct"],
                "answer_index": 0,
                "explanation": "If the loop condition never becomes false, the loop runs infinitely."
            },
            {
                "id": "loops_mcq_5",
                "question": "Loop iteration means:",
                "options": ["Resetting", "One complete run", "Copying code", "Pausing"],
                "answer_index": 1,
                "explanation": "Each iteration is one complete execution of the loop body."
            }
        ],
        "coding_questions": [
            {
                "id": "loops_code_1",
                "title": "Print Numbers 1 to N",
                "description": "Print numbers from 1 to N using a loop.",
                "sample_input": "n = 5",
                "sample_output": "1 2 3 4 5",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public void printNumbers(int n) {\n        // Write your solution here\n    }\n}"
            },
            {
                "id": "loops_code_2",
                "title": "Count Digits",
                "description": "Count the number of digits in a number using a loop.",
                "sample_input": "num = 12345",
                "sample_output": "5",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int countDigits(int num) {\n        // Write your solution here\n        return 0;\n    }\n}"
            },
            {
                "id": "loops_code_3",
                "title": "Factorial",
                "description": "Find factorial of a number using loops.",
                "sample_input": "n = 5",
                "sample_output": "120",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int factorial(int n) {\n        // Write your solution here\n        return 0;\n    }\n}"
            },
            {
                "id": "loops_code_4",
                "title": "Sum of Natural Numbers",
                "description": "Find sum of first N natural numbers.",
                "sample_input": "n = 5",
                "sample_output": "15",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int sumNatural(int n) {\n        // Write your solution here\n        return 0;\n    }\n}"
            },
            {
                "id": "loops_code_5",
                "title": "Count Even Numbers",
                "description": "Count even numbers in a given range.",
                "sample_input": "start = 1, end = 10",
                "sample_output": "5",
                "difficulty": "beginner",
                "starter_code": "public class Solution {\n    public int countEven(int start, int end) {\n        // Write your solution here\n        return 0;\n    }\n}"
            }
        ]
    }
}

def get_topic_questions(topic_name):
    """Get questions for a specific topic"""
    topic_key = topic_name.lower().replace(" ", "").replace("basics", "")
    return TOPIC_QUESTIONS.get(topic_key, {
        "mcq_questions": [],
        "coding_questions": []
    })