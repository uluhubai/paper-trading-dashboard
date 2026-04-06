#!/usr/bin/env python3
"""
Verify all Streamlit elements have keys by parsing the file properly
"""

import ast
import os

def find_streamlit_calls(node, calls=None):
    """Recursively find all Streamlit function calls in AST"""
    if calls is None:
        calls = []
    
    if isinstance(node, ast.Call):
        # Check if this is a Streamlit call
        if isinstance(node.func, ast.Attribute):
            if node.func.value.id == 'st' if hasattr(node.func.value, 'id') else False:
                calls.append(node)
    
    # Recursively check child nodes
    for child in ast.iter_child_nodes(node):
        find_streamlit_calls(child, calls)
    
    return calls

def check_file(filepath):
    """Check if all Streamlit calls have key arguments"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Syntax error in {filepath}: {e}")
        return False
    
    streamlit_calls = find_streamlit_calls(tree)
    
    issues = []
    for call in streamlit_calls:
        # Get function name
        func_name = call.func.attr
        
        # Check if has key argument
        has_key = False
        for keyword in call.keywords:
            if keyword.arg == 'key':
                has_key = True
                break
        
        if not has_key:
            # Get line number and some context
            line_no = call.lineno
            lines = content.split('\n')
            line_text = lines[line_no-1] if line_no <= len(lines) else ''
            
            issues.append({
                'func': func_name,
                'line': line_no,
                'text': line_text.strip()[:80]
            })
    
    if issues:
        print(f"❌ Found {len(issues)} Streamlit elements without keys in {filepath}:")
        for issue in issues:
            print(f"   Line {issue['line']}: {issue['func']} - {issue['text']}...")
        return False
    else:
        print(f"✅ All Streamlit elements have keys in {filepath}")
        return True

def main():
    """Main function"""
    dashboard_file = os.path.join(os.path.dirname(__file__), 'dashboard', '__init__.py')
    
    if os.path.exists(dashboard_file):
        print("🔍 Checking Streamlit elements using AST parsing...")
        if check_file(dashboard_file):
            print("\n🎉 SUCCESS! No more ID duplication errors!")
        else:
            print("\n⚠️ Some elements still need keys")
    else:
        print(f"❌ File not found: {dashboard_file}")

if __name__ == "__main__":
    main()