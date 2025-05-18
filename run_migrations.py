"""
NOUS Database Migration Runner

This script executes all required database migrations in the correct order.
It provides a unified way to update the database schema when the application is deployed.

@module: run_migrations
@author: NOUS Development Team
"""

import os
import sys
import time
import logging
import importlib.util
from typing import List, Dict, Callable, Any, Optional
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Migration configuration
MIGRATIONS = [
    {
        "module": "migrate_cache_table",
        "function": "apply_migration",
        "description": "Creating cache_entries table",
        "required": True
    },
    {
        "module": "migrate_indexes",
        "function": "apply_migrations",
        "description": "Adding database indexes for performance",
        "required": True
    },
    {
        "module": "migrate_missing_columns",
        "function": "apply_migrations",  # Fixed function name
        "description": "Adding any missing database columns",
        "required": True
    },
    {
        "module": "migrate_backup_codes",
        "function": "apply_migration",
        "description": "Updating two_factor_backup_codes table to use string user_id",
        "required": False  # Mark as optional in case the table doesn't exist yet
    },
    {
        "module": "migrate_api_keys",
        "function": "apply_migration",
        "description": "Updating api_keys table to use string user_id",
        "required": False  # Mark as optional in case the table doesn't exist yet
    },
    {
        "module": "migrate_api_key_events",
        "function": "apply_migration",
        "description": "Updating api_key_events table to use string performed_by_id",
        "required": False  # Mark as optional in case the table doesn't exist yet
    },
    {
        "module": "migrate_user_memory",
        "function": "apply_migration",
        "description": "Updating user_memory_entries table to use string user_id",
        "required": False  # Mark as optional in case the table doesn't exist yet
    }
]

def check_environment() -> bool:
    """
    Check if required environment variables are set
    
    Returns:
        bool: True if critical variables are set, False otherwise
    """
    logger.info("Checking environment variables for migrations...")
    
    # Critical environment variables
    critical_vars = ["DATABASE_URL"]
    
    # Important but not critical variables
    important_vars = ["SECRET_KEY", "SESSION_SECRET", "FLASK_ENV"]
    
    all_critical_present = True
    
    # Check critical variables
    for var_name in critical_vars:
        if os.environ.get(var_name):
            logger.info(f"✓ Critical environment variable {var_name} is set")
        else:
            logger.error(f"✗ Critical environment variable {var_name} is not set")
            all_critical_present = False
    
    # Check important variables
    for var_name in important_vars:
        if os.environ.get(var_name):
            logger.info(f"✓ Important environment variable {var_name} is set")
        else:
            logger.warning(f"! Important environment variable {var_name} is not set")
    
    return all_critical_present

def import_migration_module(module_name: str) -> Optional[Any]:
    """Import a migration module dynamically
    
    Args:
        module_name: Name of the module to import
        
    Returns:
        The imported module or None if not found
    """
    try:
        # Check if module exists
        module_path = f"{module_name}.py"
        if not os.path.exists(module_path):
            logger.error(f"Migration module not found: {module_path}")
            return None
        
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            logger.error(f"Could not load module spec: {module_name}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        return module
    except Exception as e:
        logger.error(f"Error importing migration module {module_name}: {str(e)}")
        traceback.print_exc()
        return None

def run_migrations(dry_run: bool = False) -> bool:
    """Run all migrations in order
    
    Args:
        dry_run: If True, only print what would be done but don't execute
        
    Returns:
        True if all required migrations succeeded, False otherwise
    """
    logger.info(f"Starting migrations (dry_run={dry_run})")
    
    # First check environment
    if not check_environment():
        logger.error("Environment check failed - critical variables missing")
        return False
    
    success = True
    results = []
    
    for migration in MIGRATIONS:
        module_name = migration["module"]
        function_name = migration["function"]
        description = migration["description"]
        required = migration["required"]
        
        logger.info(f"Processing migration: {description} ({module_name}.{function_name})")
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would execute {module_name}.{function_name}()")
            results.append({
                "module": module_name,
                "function": function_name,
                "description": description,
                "status": "skipped (dry run)",
                "required": required
            })
            continue
        
        # Import the module
        module = import_migration_module(module_name)
        if module is None:
            status = "failed (module not found)"
            if required:
                success = False
        else:
            # Get the migration function
            migration_func = getattr(module, function_name, None)
            status = ""  # Initialize status to avoid unbound variable error
            if migration_func is None:
                # Try to find an alternative function in the module
                alternate_funcs = [f for f in dir(module) if f.startswith('apply_')]
                if alternate_funcs:
                    logger.warning(f"Function {function_name} not found, trying alternative: {alternate_funcs[0]}")
                    migration_func = getattr(module, alternate_funcs[0])
                    function_name = alternate_funcs[0]  # Update for reporting
                else:
                    status = f"failed (function {function_name} not found and no alternatives available)"
                    if required:
                        success = False
                    migration_func = None
            
            if migration_func:
                # Run the migration
                try:
                    start_time = time.time()
                    result = migration_func()
                    end_time = time.time()
                    
                    if result is None:  # Handle functions that don't return anything
                        logger.warning(f"Migration function {function_name} returned None, assuming success")
                        status = f"success (assumed) ({(end_time - start_time):.2f}s)"
                    elif result:
                        status = f"success ({(end_time - start_time):.2f}s)"
                    else:
                        status = "failed (function returned False)"
                        if required:
                            success = False
                except Exception as e:
                    logger.error(f"  Error executing migration: {str(e)}")
                    traceback.print_exc()
                    status = f"failed (exception: {str(e)})"
                    if required:
                        success = False
        
        # Ensure status is defined in all code paths
        if 'status' not in locals():
            status = "unknown"
            
        logger.info(f"  Migration status: {status}")
        results.append({
            "module": module_name,
            "function": function_name,
            "description": description,
            "status": status,
            "required": required
        })
    
    # Print summary
    logger.info("Migration Summary:")
    for result in results:
        logger.info(f"  {result['description']}: {result['status']}")
    
    if success:
        logger.info("All required migrations completed successfully")
    else:
        logger.error("One or more required migrations failed")
    
    return success

if __name__ == "__main__":
    # Check for command-line arguments
    dry_run = "--dry-run" in sys.argv
    ignore_errors = "--ignore-errors" in sys.argv
    
    try:
        success = run_migrations(dry_run)
        if success or ignore_errors:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Unhandled exception in migration process: {str(e)}")
        traceback.print_exc()
        if ignore_errors:
            logger.warning("Ignoring errors due to --ignore-errors flag")
            sys.exit(0)
        else:
            sys.exit(2) 