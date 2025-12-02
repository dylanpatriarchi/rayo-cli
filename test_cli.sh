#!/bin/bash

# Rayo CLI - Test Script
# This script demonstrates how to test the Rayo CLI

echo "🧪 Rayo CLI Test Suite"
echo "====================="
echo ""

# Activate virtual environment
source venv/bin/activate

echo "1️⃣  Testing CLI Installation"
echo "----------------------------"
which rayo
echo ""

echo "2️⃣  Testing Help Command"
echo "------------------------"
rayo --help
echo ""

echo "3️⃣  Testing Version Command"
echo "---------------------------"
rayo version
echo ""

echo "4️⃣  Testing Configuration Wizard"
echo "--------------------------------"
echo "Run: rayo config"
echo "(This will launch the interactive setup wizard)"
echo ""

echo "5️⃣  Testing Prompt Loading"
echo "--------------------------"
python3 -c "
from rayo.prompts import load_system_prompt
prompt = load_system_prompt()
print(f'✓ Prompt loaded: {len(prompt)} characters, {len(prompt.splitlines())} lines')
print(f'First 100 chars: {prompt[:100]}...')
"
echo ""

echo "6️⃣  Testing Configuration Loading"
echo "---------------------------------"
python3 -c "
from rayo.config import load_config
try:
    config = load_config()
    print(f'✓ Config loaded')
    print(f'  Model: {config.default_model}')
    print(f'  Max tokens: {config.max_tokens}')
    print(f'  Temperature: {config.temperature}')
    print(f'  API keys configured: {len(config.api_keys)}')
except Exception as e:
    print(f'⚠ No config yet (expected on first run): {e}')
"
echo ""

echo "7️⃣  Testing Tools Import"
echo "------------------------"
python3 -c "
from rayo.tools import ListFilesTool, ReadFileTool, ApplyPatchTool, RunBashTool
print('✓ All tools imported successfully')
print(f'  - {ListFilesTool().name}')
print(f'  - {ReadFileTool().name}')
print(f'  - {ApplyPatchTool().name}')
print(f'  - {RunBashTool().name}')
"
echo ""

echo "8️⃣  Testing File System Tool"
echo "----------------------------"
python3 -c "
from rayo.tools import ListFilesTool
tool = ListFilesTool()
result = tool.execute(path='./src/rayo')
print('✓ ListFilesTool executed successfully')
print(result['output'][:500] + '...')
"
echo ""

echo "✅ All tests completed!"
echo ""
echo "📝 Next steps:"
echo "  1. Run 'rayo config' to set up your API keys"
echo "  2. Run 'rayo start' to launch the AI assistant"
echo "  3. Try asking it to list files, read code, etc."
