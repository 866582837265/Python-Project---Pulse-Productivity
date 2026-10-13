#!/usr/bin/env python3
"""
Fix Unicode characters in app.py
"""

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode characters
replacements = {
    '🔄': '',
    '❌': '',
    '✅': '',
    '⚙️': '',
    '🧪': '',
    '🏁': '',
    '🔍': '',
    '📚': '',
    '🤖': '',
    '🔧': '',
    '💾': '',
    '💻': '',
    '✨': '',
    '→': '->',
}

for unicode_char, replacement in replacements.items():
    content = content.replace(unicode_char, replacement)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Unicode characters in app.py")