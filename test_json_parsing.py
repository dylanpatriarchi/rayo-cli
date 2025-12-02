#!/usr/bin/env python3
"""Test JSON parsing from markdown code blocks."""

import re
import json

# Test the parsing logic
test_cases = [
    # Case 1: Plain JSON
    '{"tool": "list_files", "parameters": {"path": "."}, "reasoning": "Test"}',
    
    # Case 2: JSON in code block with json marker
    '''```json
{"tool": "list_files", "parameters": {"path": "."}, "reasoning": "Test"}
```''',
    
    # Case 3: JSON in code block without marker
    '''```
{"tool": "list_files", "parameters": {"path": "."}, "reasoning": "Test"}
```''',
    
    # Case 4: With text before and after
    '''Here is the command:
```json
{"tool": "list_files", "parameters": {"path": "."}, "reasoning": "Test"}
```
This will list the files.'''
]

print("Testing JSON extraction from markdown:")
print("=" * 50)

for i, test in enumerate(test_cases, 1):
    json_text = test.strip()
    
    if '```json' in json_text or '```' in json_text:
        match = re.search(r'```json\s*\n(.*?)\n```', json_text, re.DOTALL)
        if not match:
            match = re.search(r'```\s*\n(.*?)\n```', json_text, re.DOTALL)
        if match:
            json_text = match.group(1).strip()
    
    try:
        data = json.loads(json_text)
        print(f'✅ Case {i}: Parsed successfully - tool={data.get("tool")}')
    except Exception as e:
        print(f'❌ Case {i}: Failed to parse - {e}')

print("\n✅ All test cases should pass!")
