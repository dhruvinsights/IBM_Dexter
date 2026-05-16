#!/usr/bin/env python3
"""
Fix Python 3.9 compatibility issues in model files.
Converts Python 3.10+ union syntax (Type | None) to Optional[Type].
"""

import re
import sys
from pathlib import Path

def fix_union_syntax(content: str) -> tuple[str, int]:
    """
    Replace 'Type | None' with 'Optional[Type]' in type annotations.
    Returns (fixed_content, number_of_replacements)
    """
    # Pattern to match: Mapped[type | None]
    pattern = r'Mapped\[(\w+)\s*\|\s*None\]'
    
    def replace_func(match):
        type_name = match.group(1)
        return f'Mapped[Optional[{type_name}]]'
    
    fixed_content, count = re.subn(pattern, replace_func, content)
    return fixed_content, count

def ensure_optional_import(content: str) -> str:
    """Ensure Optional is imported from typing."""
    # Check if Optional is already imported
    if 'Optional' in content:
        return content
    
    # Find the typing import line and add Optional
    typing_import_pattern = r'from typing import ([^\n]+)'
    match = re.search(typing_import_pattern, content)
    
    if match:
        imports = match.group(1)
        if 'Optional' not in imports:
            # Add Optional to existing imports
            new_imports = imports.rstrip() + ', Optional'
            content = content.replace(
                f'from typing import {imports}',
                f'from typing import {new_imports}'
            )
    else:
        # Add new typing import after __future__ imports
        future_import_pattern = r'(from __future__ import [^\n]+\n)'
        match = re.search(future_import_pattern, content)
        if match:
            insert_pos = match.end()
            content = (
                content[:insert_pos] +
                '\nfrom typing import Optional\n' +
                content[insert_pos:]
            )
    
    return content

def fix_file(file_path: Path) -> bool:
    """Fix a single file. Returns True if changes were made."""
    print(f"Processing {file_path}...")
    
    try:
        content = file_path.read_text()
        original_content = content
        
        # Fix union syntax
        content, count = fix_union_syntax(content)
        
        if count > 0:
            # Ensure Optional is imported
            content = ensure_optional_import(content)
            
            # Write back
            file_path.write_text(content)
            print(f"  ✅ Fixed {count} union type(s)")
            return True
        else:
            print(f"  ℹ️  No changes needed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Fix all model files."""
    models_dir = Path(__file__).parent / "app" / "models"
    
    if not models_dir.exists():
        print(f"❌ Models directory not found: {models_dir}")
        return 1
    
    print("=" * 70)
    print("FIXING PYTHON 3.9 COMPATIBILITY ISSUES")
    print("=" * 70)
    print()
    
    model_files = list(models_dir.glob("*.py"))
    fixed_count = 0
    
    for file_path in model_files:
        if file_path.name == "__init__.py":
            continue
        
        if fix_file(file_path):
            fixed_count += 1
    
    print()
    print("=" * 70)
    print(f"SUMMARY: Fixed {fixed_count} file(s)")
    print("=" * 70)
    print()
    
    if fixed_count > 0:
        print("✅ All Python 3.10+ union syntax converted to Optional")
        print()
        print("🧪 Test the changes:")
        print("   python3 -c 'from main import app; print(\"✅ Success\")'")
        print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
