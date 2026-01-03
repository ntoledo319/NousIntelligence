#!/usr/bin/env python3
"""
Migration Script: Remove Therapeutic Logging Artifacts
Phase 4.1 Code Quality - Replace therapeutic-style logging with standard logging

This script:
1. Removes decorators like @with_therapy_session, @cognitive_reframe, @stop_skill
2. Removes emoji from log messages
3. Standardizes error messages
4. Updates to use logging_config_clean.py

Usage:
    python scripts/migrate_therapeutic_logging.py --dry-run
    python scripts/migrate_therapeutic_logging.py --apply
"""
import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

# Therapeutic decorators to remove
THERAPEUTIC_DECORATORS = [
    '@with_therapy_session',
    '@cognitive_reframe',
    '@stop_skill',
    '@emotional_check_in',
    '@mindful_execution',
    '@compassionate_error_handler'
]

# Emoji patterns to remove from logs
EMOJI_PATTERN = re.compile(
    r'[\U0001F600-\U0001F64F'  # Emoticons
    r'\U0001F300-\U0001F5FF'   # Symbols & Pictographs
    r'\U0001F680-\U0001F6FF'   # Transport & Map
    r'\U0001F1E0-\U0001F1FF'   # Flags
    r'\U00002702-\U000027B0'
    r'\U000024C2-\U0001F251]+',
    re.UNICODE
)

def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in the project"""
    python_files = []
    root = Path(root_dir)
    
    # Exclude certain directories
    exclude_dirs = {'venv', 'env', '.venv', 'node_modules', '__pycache__', '.git'}
    
    for py_file in root.rglob('*.py'):
        if not any(excluded in py_file.parts for excluded in exclude_dirs):
            python_files.append(py_file)
    
    return python_files

def clean_file(file_path: Path, dry_run: bool = True) -> Tuple[bool, int]:
    """
    Clean a single file
    
    Returns:
        (changed, num_changes): Whether file was changed and number of changes
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    content = original_content
    changes = 0
    
    # Remove therapeutic decorators
    for decorator in THERAPEUTIC_DECORATORS:
        if decorator in content:
            # Remove decorator line (including arguments)
            pattern = rf'{re.escape(decorator)}\([^)]*\)\s*\n'
            content, count = re.subn(pattern, '', content)
            changes += count
            
            # Remove decorator without arguments
            pattern = rf'{re.escape(decorator)}\s*\n'
            content, count = re.subn(pattern, '', content)
            changes += count
    
    # Remove emoji from log messages
    log_patterns = [
        r'logger\.(debug|info|warning|error|critical)\([\'"]',
        r'logging\.(debug|info|warning|error|critical)\([\'"]',
        r'print\([\'"]'
    ]
    
    for pattern in log_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Find the end of the string
            start = match.end()
            quote_char = content[start - 1]
            end = content.find(quote_char, start)
            
            if end != -1:
                log_message = content[start:end]
                cleaned_message = EMOJI_PATTERN.sub('', log_message).strip()
                
                if cleaned_message != log_message:
                    content = content[:start] + cleaned_message + content[end:]
                    changes += 1
    
    # Replace therapeutic error messages
    therapeutic_patterns = {
        r'A learning opportunity has appeared': 'An error occurred',
        r'The journey encounters an obstacle': 'Error encountered',
        r'cosmic convergence': 'initialization',
        r'sacred process': 'process',
        r'manifested into existence': 'created',
        r'with intention': '',
        r'with love': '',
    }
    
    for pattern, replacement in therapeutic_patterns.items():
        content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
        changes += count
    
    # Only write if changes were made
    if content != original_content:
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return True, changes
    
    return False, 0

def main():
    parser = argparse.ArgumentParser(
        description='Migrate therapeutic logging to standard logging'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply changes (default is dry-run)'
    )
    parser.add_argument(
        '--root',
        default='.',
        help='Root directory to scan (default: current directory)'
    )
    
    args = parser.parse_args()
    dry_run = not args.apply
    
    print(f"{'DRY RUN: ' if dry_run else ''}Scanning for therapeutic logging artifacts...")
    
    python_files = find_python_files(args.root)
    print(f"Found {len(python_files)} Python files to check")
    
    total_changes = 0
    files_changed = 0
    
    for file_path in python_files:
        changed, num_changes = clean_file(file_path, dry_run)
        if changed:
            files_changed += 1
            total_changes += num_changes
            print(f"{'Would clean' if dry_run else 'Cleaned'} {file_path}: {num_changes} changes")
    
    print(f"\nSummary:")
    print(f"Files {'that would be' if dry_run else ''} changed: {files_changed}")
    print(f"Total changes: {total_changes}")
    
    if dry_run:
        print("\nRun with --apply to make actual changes")

if __name__ == '__main__':
    main()
