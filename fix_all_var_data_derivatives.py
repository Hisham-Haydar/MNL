"""
Fix ALL var_data None checks in estimation_engine.py - Complete Version
Adds None checks to BOTH mu_w calculations AND derivative calculations
"""

import re

def fix_all_var_data_issues():
    filepath = r"U:\Desktop\Nizam_Hisham\MNL\scripts\enhanced\estimation_engine.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements_made = 0
    
    # =========================================================================
    # Pattern 1: Fix derivative calculations (THE MAIN ISSUE)
    # =========================================================================
    # Pattern: deriv = residual / sigma * var_data
    # Fix: Add None check before this line
    
    pattern1 = r'(\s+)(var_data = getattr\(data, var_name.*?\))\n(\s+)(deriv = .*? \* var_data)'
    
    def replacement1(match):
        indent1 = match.group(1)
        getattr_line = match.group(2)
        indent2 = match.group(3)
        deriv_line = match.group(4)
        
        return f'''{indent1}{getattr_line}
{indent2}if var_data is not None:
{indent2}    {deriv_line}
{indent2}else:
{indent2}    continue'''
    
    content, count1 = re.subn(pattern1, replacement1, content, flags=re.MULTILINE)
    replacements_made += count1
    print(f"Fixed {count1} derivative calculations with simple pattern")
    
    # =========================================================================
    # Pattern 2: Fix derivative with gender suffix
    # =========================================================================
    # Pattern: var_data = getattr(data, var_name_gender)
    #          deriv = residual / sigma * var_data
    
    pattern2 = r'(\s+)(var_name_gender = f"\{var_name\}\{suffix\}")\n(\s+)(if hasattr\(data, var_name_gender\):)\n(\s+)(var_data = getattr\(data, var_name_gender\))\n(\s+)(deriv = .*? \* var_data)'
    
    def replacement2(match):
        indent1 = match.group(1)
        varname_line = match.group(2)
        indent3 = match.group(3)
        hasattr_line = match.group(4)
        indent5 = match.group(5)
        getattr_line = match.group(6)
        indent7 = match.group(7)
        deriv_line = match.group(8)
        
        return f'''{indent1}{varname_line}
{indent3}{hasattr_line}
{indent5}{getattr_line}
{indent7}if var_data is not None:
{indent7}    {deriv_line}
{indent7}else:
{indent7}    continue'''
    
    content, count2 = re.subn(pattern2, replacement2, content, flags=re.MULTILINE)
    replacements_made += count2
    print(f"Fixed {count2} derivative calculations with gender suffix")
    
    # =========================================================================
    # Pattern 3: Fix deriv += var_data * ... patterns (couples)
    # =========================================================================
    # Pattern: var_data = getattr(data, var_name_...)
    #          deriv += var_data * bc_l_...
    
    pattern3 = r'(\s+)(var_data = getattr\(data, var_name.*?\))\n(\s+)(deriv \+= var_data \* .*)'
    
    def replacement3(match):
        indent1 = match.group(1)
        getattr_line = match.group(2)
        indent2 = match.group(3)
        deriv_line = match.group(4)
        
        return f'''{indent1}{getattr_line}
{indent2}if var_data is not None:
{indent2}    {deriv_line}'''
    
    content, count3 = re.subn(pattern3, replacement3, content, flags=re.MULTILINE)
    replacements_made += count3
    print(f"Fixed {count3} deriv += calculations")
    
    # =========================================================================
    # Pattern 4: Fix deriv_common calculations with loc_indicator
    # =========================================================================
    # Pattern: deriv_common += residual_g / sigma_g * var_data * loc_indicator
    # This one already has var_data defined earlier, just needs None check
    
    pattern4 = r'(\s+)(deriv_common \+= residual_g / sigma_g \* var_data \* loc_indicator)'
    
    def replacement4(match):
        indent = match.group(1)
        deriv_line = match.group(2)
        
        return f'''{indent}if var_data is not None:
{indent}    {deriv_line}'''
    
    content, count4 = re.subn(pattern4, replacement4, content, flags=re.MULTILINE)
    replacements_made += count4
    print(f"Fixed {count4} deriv_common calculations")
    
    # Save the file
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ SUCCESS! Made {replacements_made} total replacements")
        print(f"Fixed file: {filepath}")
    else:
        print("\n⚠️ No changes made - patterns might already be fixed")
    
    return replacements_made

if __name__ == "__main__":
    print("=" * 80)
    print("Fixing ALL var_data None checks in estimation_engine.py")
    print("=" * 80)
    count = fix_all_var_data_issues()
    print("=" * 80)
    print(f"COMPLETE - {count} fixes applied")
    print("=" * 80)
