#!/usr/bin/env python
"""Fix parameter names in RURO_post_estimation.py - update to simplified model"""

import re

filepath = "RURO_post_estimation.py"

# Read the file
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements for parameter names
replacements = [
    # Single males
    ('"beta_l_log_age": params.get("sm.pref.beta_l_log_age", 0.0),',
     '"beta_l_age_norm": params.get("sm.pref.beta_l_age_norm", 0.0),'),
    ('"beta_l_log_age2": params.get("sm.pref.beta_l_log_age2", 0.0),',
     '"beta_l_age_norm2": params.get("sm.pref.beta_l_age_norm2", 0.0),'),
    ('"beta_l_ch4_6": params.get("sm.pref.beta_l_ch4_6", 0.0),',
     '"beta_l_n_children": params.get("sm.pref.beta_l_n_children", 0.0),'),
    # Remove these lines for sm
    ('"beta_l_ch7_9": params.get("sm.pref.beta_l_ch7_9", 0.0),\n', ''),
    ('"beta_l_reg2": params.get("sm.pref.beta_l_reg2", 0.0),\n', ''),
    ('"beta_l_ch0_3": params.get("sm.pref.beta_l_ch0_3", 0.0),  # typically 0 for males\n', ''),
    
    # Single females
    ('"beta_l_log_age": params.get("sf.pref.beta_l_log_age", 0.0),',
     '"beta_l_age_norm": params.get("sf.pref.beta_l_age_norm", 0.0),'),
    ('"beta_l_log_age2": params.get("sf.pref.beta_l_log_age2", 0.0),',
     '"beta_l_age_norm2": params.get("sf.pref.beta_l_age_norm2", 0.0),'),
    ('"beta_l_ch4_6": params.get("sf.pref.beta_l_ch4_6", 0.0),',
     '"beta_l_n_children": params.get("sf.pref.beta_l_n_children", 0.0),'),
    # Remove these lines for sf
    ('"beta_l_ch7_9": params.get("sf.pref.beta_l_ch7_9", 0.0),\n', ''),
    ('"beta_l_reg2": params.get("sf.pref.beta_l_reg2", 0.0),\n', ''),
    ('"beta_l_reg3": params.get("sf.pref.beta_l_reg3", 0.0),\n', ''),
    ('"beta_l_ch0_3": params.get("sf.pref.beta_l_ch0_3", 0.0),\n', ''),
    
    # Couples male
    ('"beta_l_log_age": params.get("cou.pref.beta_l_log_age_m", 0.0),',
     '"beta_l_age_norm": params.get("cou.pref.beta_l_age_norm_m", 0.0),'),
    ('"beta_l_log_age2": params.get("cou.pref.beta_l_log_age2_m", 0.0),',
     '"beta_l_age_norm2": params.get("cou.pref.beta_l_age_norm2_m", 0.0),'),
    ('"beta_l_ch0_3": params.get("cou.pref.beta_l_ch0_3_m", 0.0),',
     '"beta_l_n_children": params.get("cou.pref.beta_l_n_children_m", 0.0),'),
    # Remove these lines for cou_m
    ('"beta_l_ch4_6": params.get("cou.pref.beta_l_ch4_6_m", 0.0),\n', ''),
    ('"beta_l_ch7_9": params.get("cou.pref.beta_l_ch7_9_m", 0.0),\n', ''),
    ('"beta_l_reg2": params.get("cou.pref.beta_l_reg2_m", 0.0),\n', ''),
    ('"beta_l_reg3": params.get("cou.pref.beta_l_reg3_m", 0.0),\n', ''),
    
    # Couples female
    ('"beta_l_log_age": params.get("cou.pref.beta_l_log_age_f", 0.0),',
     '"beta_l_age_norm": params.get("cou.pref.beta_l_age_norm_f", 0.0),'),
    ('"beta_l_log_age2": params.get("cou.pref.beta_l_log_age2_f", 0.0),',
     '"beta_l_age_norm2": params.get("cou.pref.beta_l_age_norm2_f", 0.0),'),
    ('"beta_l_ch0_3": params.get("cou.pref.beta_l_ch0_3_f", 0.0),',
     '"beta_l_n_children": params.get("cou.pref.beta_l_n_children_f", 0.0),'),
    # Remove these lines for cou_f
    ('"beta_l_ch4_6": params.get("cou.pref.beta_l_ch4_6_f", 0.0),\n', ''),
    ('"beta_l_ch7_9": params.get("cou.pref.beta_l_ch7_9_f", 0.0),\n', ''),
    ('"beta_l_reg2": params.get("cou.pref.beta_l_reg2_f", 0.0),\n', ''),
    ('"beta_l_reg3": params.get("cou.pref.beta_l_reg3_f", 0.0),\n', ''),
    
    # Remove beta_interaction
    ('"beta_interaction": params.get("cou.pref.beta_interaction", 0.0),\n', ''),
    
    # Update comments
    ('# Extract single males\n', '# Extract single males - SIMPLIFIED MODEL (age_norm, n_children)\n'),
    ('# Extract single females\n', '# Extract single females - SIMPLIFIED MODEL (age_norm, n_children)\n'),
    ('# Extract couples - male leisure\n', '# Extract couples - male leisure - SIMPLIFIED MODEL\n'),
    ('# Extract couples - female leisure\n', '# Extract couples - female leisure - SIMPLIFIED MODEL\n'),
]

for old, new in replacements:
    count = content.count(old)
    if count > 0:
        print(f"Replacing {count} occurrences: {old[:50]}...")
        content = content.replace(old, new)

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone! Verifying...")

# Verify
with open(filepath, 'r', encoding='utf-8') as f:
    new_content = f.read()
    
# Check for old vs new param names
old_count = new_content.count("beta_l_log_age")
new_count = new_content.count("beta_l_age_norm")
print(f"Old param name (beta_l_log_age) occurrences: {old_count}")
print(f"New param name (beta_l_age_norm) occurrences: {new_count}")
