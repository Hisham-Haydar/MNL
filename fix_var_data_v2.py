"""
Safer fix for var_data None checks
Only modifies lines where params[coef_name] * var_data is used
"""

# Read the file
with open('scripts/enhanced/estimation_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track modifications
modified = 0

# Process line by line
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line contains the problematic pattern
    if 'params[coef_name] * var_data' in line and 'if var_data is not None:' not in lines[i-1] if i > 0 else True:
        # Check previous line has var_data = getattr
        if i > 0 and 'var_data = getattr(' in lines[i-1]:
            # Get the indentation of current line
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            
            # Insert None check before this line
            none_check = f"{indent}if var_data is not None:\n"
            # Increase indentation of current line
            new_line = f"{indent}    {stripped}"
            
            # Replace current line
            lines[i] = none_check + new_line
            modified += 1
    
    i += 1

# Write back
with open('scripts/enhanced/estimation_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✅ Fixed {modified} occurrences of var_data usage")
