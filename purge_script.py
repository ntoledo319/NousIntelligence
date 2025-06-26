#!/usr/bin/env python3
"""
DUPLICATE & DEAD-WEIGHT PURGE SCRIPT
Removes duplicate and dead files identified by the codebase analyzer
"""

import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Set

def load_codegraph() -> Dict:
    """Load the generated code graph"""
    with open('/tmp/codegraph.json', 'r') as f:
        return json.load(f)

def create_purge_backup(files_to_remove: List[str]) -> None:
    """Create backup of files before purging"""
    backup_dir = Path('backup/purge_operation')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Creating backup in {backup_dir}")
    
    for file_path in files_to_remove:
        if Path(file_path).exists():
            # Preserve directory structure in backup
            backup_path = backup_dir / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            print(f"  Backed up: {file_path}")

def analyze_dead_files(dead_files: List[str], routes: List[Dict], models: List[Dict]) -> Dict:
    """Analyze dead files to categorize them"""
    
    # Files that are definitely safe to remove
    safe_to_remove = []
    
    # Files that might be used dynamically
    maybe_used = []
    
    # Files that should be kept for safety
    keep_for_safety = []
    
    # Core files that should never be removed
    core_files = {
        'main.py', 'config.py', 'database.py', 'models.py', 
        'minimal_public_app.py', 'nous_surgical_app.py',
        'surgical_nous_app.py', 'replit.toml', 'pyproject.toml'
    }
    
    for file_path in dead_files:
        file_name = Path(file_path).name
        
        # Never remove core files
        if file_name in core_files:
            keep_for_safety.append(file_path)
            continue
            
        # Remove obvious dead files
        if any(pattern in file_path for pattern in [
            'test_', '__pycache__', '.pyc', '.log', 
            'backup/', 'temp/', '.tmp'
        ]):
            safe_to_remove.append(file_path)
            continue
            
        # Templates might be used dynamically
        if 'templates/' in file_path:
            maybe_used.append(file_path)
            continue
            
        # Utility files might be imported dynamically
        if 'utils/' in file_path:
            maybe_used.append(file_path)
            continue
            
        # Static files might be referenced in templates
        if 'static/' in file_path:
            maybe_used.append(file_path)
            continue
            
        # Routes and models directories
        if 'routes/' in file_path or 'models/' in file_path:
            maybe_used.append(file_path)
            continue
            
        # Everything else is potentially safe to remove
        safe_to_remove.append(file_path)
    
    return {
        'safe_to_remove': safe_to_remove,
        'maybe_used': maybe_used,
        'keep_for_safety': keep_for_safety
    }

def remove_duplicate_files(duplicates: Dict[str, List[str]]) -> None:
    """Remove duplicate files, keeping the shortest path"""
    print("🔄 Processing duplicate files...")
    
    removed_count = 0
    
    for hash_val, file_paths in duplicates.items():
        if len(file_paths) <= 1:
            continue
            
        # Sort by path length (keep shortest path)
        file_paths.sort(key=len)
        keep_file = file_paths[0]
        remove_files = file_paths[1:]
        
        print(f"  Keeping: {keep_file}")
        
        for remove_file in remove_files:
            if Path(remove_file).exists():
                print(f"  Removing duplicate: {remove_file}")
                os.remove(remove_file)
                removed_count += 1
    
    print(f"✅ Removed {removed_count} duplicate files")

def remove_safe_dead_files(safe_files: List[str]) -> None:
    """Remove files that are safe to delete"""
    print("💀 Removing safe dead files...")
    
    removed_count = 0
    
    for file_path in safe_files:
        if Path(file_path).exists():
            print(f"  Removing: {file_path}")
            os.remove(file_path)
            removed_count += 1
    
    # Clean up empty directories
    for root, dirs, files in os.walk('.', topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"  Removed empty directory: {dir_path}")
            except OSError:
                pass
    
    print(f"✅ Removed {removed_count} dead files")

def create_purge_report(analysis: Dict, duplicates: Dict) -> None:
    """Create a report of the purge operation"""
    report_path = 'docs/purge_report.md'
    
    with open(report_path, 'w') as f:
        f.write("# CODEBASE PURGE OPERATION REPORT\n\n")
        f.write(f"Generated: {os.popen('date').read().strip()}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Duplicate groups processed**: {len(duplicates)}\n")
        f.write(f"- **Safe files removed**: {len(analysis['safe_to_remove'])}\n")
        f.write(f"- **Files kept for safety**: {len(analysis['keep_for_safety'])}\n")
        f.write(f"- **Files requiring review**: {len(analysis['maybe_used'])}\n\n")
        
        if analysis['safe_to_remove']:
            f.write("## Files Removed (Safe)\n\n")
            for file_path in analysis['safe_to_remove']:
                f.write(f"- `{file_path}`\n")
            f.write("\n")
        
        if analysis['maybe_used']:
            f.write("## Files Requiring Manual Review\n\n")
            f.write("These files appear unused but might be referenced dynamically:\n\n")
            for file_path in analysis['maybe_used']:
                f.write(f"- `{file_path}`\n")
            f.write("\n")
        
        if analysis['keep_for_safety']:
            f.write("## Files Kept for Safety\n\n")
            for file_path in analysis['keep_for_safety']:
                f.write(f"- `{file_path}`\n")
            f.write("\n")
    
    print(f"📄 Purge report saved to {report_path}")

def main():
    """Main purge operation"""
    print("🚀 Starting DUPLICATE & DEAD-WEIGHT PURGE...")
    
    # Load code graph
    codegraph = load_codegraph()
    
    # Analyze dead files
    analysis = analyze_dead_files(
        codegraph['dead_files'],
        codegraph['routes'],
        codegraph['models']
    )
    
    print(f"\n📊 PURGE ANALYSIS:")
    print(f"  Safe to remove: {len(analysis['safe_to_remove'])}")
    print(f"  Maybe used: {len(analysis['maybe_used'])}")
    print(f"  Keep for safety: {len(analysis['keep_for_safety'])}")
    
    # Create backup of files to be removed
    files_to_backup = analysis['safe_to_remove']
    if files_to_backup:
        create_purge_backup(files_to_backup)
    
    # Remove duplicates
    remove_duplicate_files(codegraph['duplicates'])
    
    # Remove safe dead files
    remove_safe_dead_files(analysis['safe_to_remove'])
    
    # Create report
    create_purge_report(analysis, codegraph['duplicates'])
    
    print("\n✅ PURGE OPERATION COMPLETE")
    print("📄 Review the purge report for details")
    print("📦 Backups created in backup/purge_operation/")

if __name__ == "__main__":
    main()