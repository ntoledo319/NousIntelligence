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
from typing import List, Dict, Callable, Any

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
        "function": "apply_migrations",
        "description": "Adding any missing database columns",
        "required": True
    },
    {
        "module": "migrate_backup_codes",
        "function": "apply_migration",
        "description": "Updating two_factor_backup_codes table to use string user_id",
        "required": True
    },
    {
        "module": "migrate_api_keys",
        "function": "apply_migration",
        "description": "Updating api_keys table to use string user_id",
        "required": True
    },
    {
        "module": "migrate_api_key_events",
        "function": "apply_migration",
        "description": "Updating api_key_events table to use string performed_by_id",
        "required": True
    }
]

def import_migration_module(module_name: str) -> Any:
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
        return None

def run_migrations(dry_run: bool = False) -> bool:
    """Run all migrations in order
    
    Args:
        dry_run: If True, only print what would be done but don't execute
        
    Returns:
        True if all required migrations succeeded, False otherwise
    """
    logger.info(f"Starting migrations (dry_run={dry_run})")
    
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
            if migration_func is None:
                status = f"failed (function {function_name} not found)"
                if required:
                    success = False
            else:
                # Run the migration
                try:
                    start_time = time.time()
                    result = migration_func()
                    end_time = time.time()
                    
                    if result:
                        status = f"success ({(end_time - start_time):.2f}s)"
                    else:
                        status = "failed (function returned False)"
                        if required:
                            success = False
                except Exception as e:
                    logger.error(f"  Error executing migration: {str(e)}")
                    status = f"failed (exception: {str(e)})"
                    if required:
                        success = False
        
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
    # Check for dry run flag
    dry_run = "--dry-run" in sys.argv
    
    if run_migrations(dry_run):
        sys.exit(0)
    else:
        sys.exit(1) 