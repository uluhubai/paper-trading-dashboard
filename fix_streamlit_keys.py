#!/usr/bin/env python3
"""
Fix Streamlit elements by adding unique keys
"""

import re
import os

def add_keys_to_file(filepath):
    """Add keys to all Streamlit elements in a file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Track element counts for unique keys
    element_counts = {}
    
    # Patterns for different Streamlit elements
    patterns = [
        (r'(st\.selectbox\()', 'selectbox'),
        (r'(st\.slider\()', 'slider'),
        (r'(st\.number_input\()', 'number_input'),
        (r'(st\.text_input\()', 'text_input'),
        (r'(st\.checkbox\()', 'checkbox'),
        (r'(st\.radio\()', 'radio'),
        (r'(st\.multiselect\()', 'multiselect'),
        (r'(st\.date_input\()', 'date_input'),
        (r'(st\.time_input\()', 'time_input'),
        (r'(st\.file_uploader\()', 'file_uploader'),
        (r'(st\.color_picker\()', 'color_picker'),
    ]
    
    modified = False
    
    for pattern, element_type in patterns:
        # Find all occurrences
        matches = list(re.finditer(pattern, content))
        
        for i, match in enumerate(matches):
            # Find the closing parenthesis for this element
            start = match.start()
            depth = 0
            end = start
            
            # Find the matching closing parenthesis
            for j, char in enumerate(content[start:], start):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break
            
            element_text = content[start:end]
            
            # Check if already has a key
            if 'key=' in element_text:
                continue
            
            # Add key parameter
            # Insert before the closing parenthesis
            new_element = element_text[:-1] + f', key="{element_type}_{i}"' + element_text[-1]
            
            # Replace in content
            content = content[:start] + new_element + content[end:]
            
            # Update end position for next iteration
            end = start + len(new_element)
            modified = True
    
    if modified:
        # Backup original file
        backup_path = filepath + '.backup'
        with open(backup_path, 'w') as f:
            f.write(open(filepath).read())
        
        # Write modified content
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✅ Modified {filepath}")
        print(f"   Backup saved to {backup_path}")
        return True
    
    return False

def main():
    """Main function"""
    dashboard_file = os.path.join(os.path.dirname(__file__), 'dashboard', '__init__.py')
    
    if os.path.exists(dashboard_file):
        print(f"🔧 Fixing Streamlit elements in {dashboard_file}")
        if add_keys_to_file(dashboard_file):
            print("✅ All Streamlit elements now have unique keys!")
        else:
            print("ℹ️ No changes needed - all elements already have keys")
    else:
        print(f"❌ File not found: {dashboard_file}")

if __name__ == "__main__":
    main()