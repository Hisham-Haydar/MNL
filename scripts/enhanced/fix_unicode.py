"""Quick script to replace Unicode symbols with ASCII for PowerShell compatibility"""
from pathlib import Path

test_file = Path("scripts/enhanced/test_gamspy_benchmark.py")

# Read with UTF-8
content = test_file.read_text(encoding='utf-8')

# Replace Unicode symbols
replacements = {
    '✓': '[OK]',
    '✗': '[X]',
    '⚠': '[!]',
    '⊘': '[-]',
    'ℹ': '[i]'
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Write back with UTF-8
test_file.write_text(content, encoding='utf-8')
print(f"Fixed Unicode symbols in {test_file}")
