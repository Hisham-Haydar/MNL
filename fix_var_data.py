"""
Fix all None checks in estimation_engine.py
Adds `if var_data is not None:` check before using var_data
"""

import re

# Read the file
with open('scripts/enhanced/estimation_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find: var_data = getattr(...) followed by usage
# We need to add None check before the usage

# Find all occurrences where var_data is used without None check
lines = content.split('\n')
new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this line gets var_data from getattr
    if 'var_data = getattr(data' in line:
        # Add this line
        new_lines.append(line)
        i += 1
        
        # Check next line - if it uses var_data for multiplication, add None check
        if i < len(lines) and 'params[coef_name] * var_data' in lines[i]:
            # Get indentation of the multiplication line
            indent = len(lines[i]) - len(lines[i].lstrip())
            spaces = ' ' * indent
            
            # Check if there's already a None check
            if 'if var_data is not None:' not in lines[i-1]:
                # Add None check before the multiplication
                new_lines.append(f"{spaces}if var_data is not None:")
                new_lines.append(' ' * 4 + lines[i])  # Add extra 4 spaces for indentation
                i += 1
                continue
    
    new_lines.append(line)
    i += 1

# Write back
with open('scripts/enhanced/estimation_engine.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("✅ Fixed all var_data None checks in estimation_engine.py")
print(f"   Processed {len(lines)} lines")
