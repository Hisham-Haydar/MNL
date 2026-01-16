"""
Fix all indentation issues in gamspy_estimation.py
"""
import re

# Read the file
with open('scripts/enhanced/gamspy_estimation.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix lines with 2 extra spaces at the start
fixed_lines = []
for i, line in enumerate(lines, 1):
    # Check if line has exactly 2 extra spaces at the beginning
    # (pattern: starts with even number of spaces > expected)
    match = re.match(r'^( {2,})(\S)', line)
    if match:
        spaces = match.group(1)
        # If there are 2 extra spaces (e.g., 6 instead of 4, 10 instead of 8)
        if len(spaces) % 4 == 2:
            # Remove 2 spaces
            fixed_line = ' ' * (len(spaces) - 2) + line[len(spaces):]
            fixed_lines.append(fixed_line)
            print(f"Line {i}: Fixed indentation (had {len(spaces)} spaces)")
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write back
with open('scripts/enhanced/gamspy_estimation.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("\nDone! Fixed all indentation issues.")
