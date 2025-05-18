#!/usr/bin/env python3
"""
NOUS Database Migration Manager

This module provides a unified approach to running all database migrations
for the NOUS application. It handles errors gracefully and applies migrations
in a specific order to ensure database consistency.

Usage:
  python run_migrations.py [--dry-run] [--debug]

Options:
  --dry-run    Only check what would be done without actually modifying the database
  --debug      Show verbose debug output

Author: NOUS Development Team
"""

import os
import sys
import time
import logging
import argparse
import importlib
from typing import List, Tuple, Optional, Dict, Any, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# List of migration modules to run in specific order
MIGRATIONS = [
    # Core schema migrations first
    ('migrate_cache_table', 'apply_migration', 'Creating cache_entries table'),
    ('migrate_missing_columns', 'apply_migration', 'Ensuring all required columns exist'),
    ('migrate_color_theme', 'add_color_theme_column', 'Adding color_theme column to UserSettings'),
    
    # Foreign key migrations
    ('migrate_api_keys', 'apply_migration', 'Updating api_keys table schema'),
    ('migrate_api_key_events', 'apply_migration', 'Updating api_key_events table schema'),
    ('migrate_backup_codes', 'apply_migration', 'Updating two_factor_backup_codes table schema'),
    
    # Performance optimizations last
    ('migrate_indexes', 'apply_migrations', 'Adding database indexes for performance'),
]

def load_migration_module(module_name: str) -> Optional[Any]:
    """
    Load a migration module by name
    
    Args:
        module_name: Name of the module to load
        
    Returns:
        Optional[Any]: Loaded module or None if not found
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        logger.warning(f"Migration module {module_name} not found: {str(e)}")
        return None

def run_migration(module_name: str, function_name: str, description: str, dry_run: bool = False) -> bool:
    """
    Run a specific migration
    
    Args:
        module_name: Name of the migration module
        function_name: Name of the function within the module to call
        description: Human-readable description of the migration
        dry_run: If True, only log what would be done
        
    Returns:
        bool: True if migration succeeded, False otherwise
    """
    start_time = time.time()
    
    try:
        # Load the module
        module = load_migration_module(module_name)
        if module is None:
            logger.warning(f"Skipping migration '{description}' - module not found")
            return False
            
        # Get the migration function
        if not hasattr(module, function_name):
            logger.warning(f"Skipping migration '{description}' - function {function_name} not found in {module_name}")
            return False
            
        migration_function = getattr(module, function_name)
        
        # Run the migration (with dry_run if supported)
        if dry_run:
            # Try to call with dry_run parameter if supported
            try:
                result = migration_function(dry_run=True)
                logger.info(f"Dry run of migration '{description}' completed successfully")
            except TypeError:
                # Function doesn't support dry_run parameter
                logger.info(f"Would run migration '{description}' (no dry-run support)")
                result = True
        else:
            # Actually run the migration
            result = migration_function()
            
        end_time = time.time()
        elapsed = end_time - start_time
        
        if result:
            logger.info(f"Migration '{description}' completed successfully in {elapsed:.2f}s")
        else:
            logger.warning(f"Migration '{description}' was skipped after {elapsed:.2f}s")
            
        return True  # Count as success even if skipped
        
    except Exception as e:
        end_time = time.time()
        elapsed = end_time - start_time
        logger.error(f"Migration '{description}' failed after {elapsed:.2f}s: {str(e)}")
        return False

def check_environment() -> bool:
    """
    Check if required environment variables are set
    
    Returns:
        bool: True if all required variables are set
    """
    logger.info("Checking environment variables for migrations...")
    
    # Critical variables - migrations will fail without these
    if os.environ.get('DATABASE_URL'):
        logger.info("✓ Critical environment variable DATABASE_URL is set")
    else:
        logger.error("✗ Critical environment variable DATABASE_URL is not set")
        return False
        
    # Important but not critical variables
    for var in ['SECRET_KEY', 'SESSION_SECRET', 'FLASK_ENV']:
        if os.environ.get(var):
            logger.info(f"✓ Important environment variable {var} is set")
        else:
            logger.warning(f"! Important environment variable {var} is not set")
    
    return True

def run_all_migrations(dry_run: bool = False) -> bool:
    """
    Run all migrations in sequence
    
    Args:
        dry_run: If True, only log what would be done without modifying the database
        
    Returns:
        bool: True if all migrations succeeded, False if any failed
    """
    logger.info(f"Starting migrations (dry_run={dry_run})")
    
    # Check environment first
    if not check_environment():
        logger.error("Environment check failed, cannot run migrations")
        return False
    
    start_time = time.time()
    success_count = 0
    fail_count = 0
    
    # Run all migrations in order
    for i, (module_name, function_name, description) in enumerate(MIGRATIONS):
        migration_number = i + 1
        logger.info(f"Running migration {migration_number}/{len(MIGRATIONS)}: {description}")
        
        if run_migration(module_name, function_name, description, dry_run):
            success_count += 1
        else:
            fail_count += 1
    
    # Log summary
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info(f"Migration summary: {success_count} succeeded, {fail_count} failed, in {total_time:.2f}s")
    
    # Return True if all succeeded
    return fail_count == 0

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="NOUS Database Migration Manager")
    parser.add_argument('--dry-run', action='store_true', help='Only check migrations without modifying the database')
    parser.add_argument('--debug', action='store_true', help='Show detailed debug output')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled - showing verbose output")
    
    # Run migrations
    success = run_all_migrations(args.dry_run)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)