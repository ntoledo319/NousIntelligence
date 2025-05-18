"""
Maintenance utilities for optimizing database and cache performance.
Provides scheduled jobs to clean up and maintain system resources.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Global state for tracking maintenance tasks
_last_run_times: Dict[str, datetime] = {}
_maintenance_thread = None
_maintenance_lock = threading.RLock()
_should_run = False

def start_maintenance_scheduler():
    """Start the background maintenance scheduler if not already running."""
    global _maintenance_thread, _should_run
    
    with _maintenance_lock:
        if _maintenance_thread is None or not _maintenance_thread.is_alive():
            _should_run = True
            _maintenance_thread = threading.Thread(target=_maintenance_worker, daemon=True)
            _maintenance_thread.start()
            logging.info("Started maintenance scheduler")

def stop_maintenance_scheduler():
    """Stop the maintenance scheduler."""
    global _should_run
    
    with _maintenance_lock:
        _should_run = False
        if _maintenance_thread and _maintenance_thread.is_alive():
            _maintenance_thread.join(timeout=5.0)
            logging.info("Stopped maintenance scheduler")

def _maintenance_worker():
    """Background worker that runs maintenance tasks at scheduled intervals."""
    while _should_run:
        try:
            # Sleep for a short while before starting tasks
            time.sleep(2)
            
            # Initialize context variable
            context = None
            
            try:
                # Try to import flask components
                from flask import current_app, has_app_context
                
                if has_app_context():
                    # We're already in an app context
                    pass
                else:
                    try:
                        # Try to get app context from current_app
                        context = current_app.app_context()
                        context.__enter__()
                    except RuntimeError:
                        # Can't get a Flask app context
                        logging.warning("Running maintenance tasks without app context")
                        
                # Check each task and run if due
                now = datetime.utcnow()
                
                # Task 1: Knowledge base pruning (every 24 hours)
                _run_task_if_due('prune_knowledge_base', now, hours=24, func=_prune_knowledge_base)
                
                # Task 2: Cache cleanup (every 6 hours)
                _run_task_if_due('clean_caches', now, hours=6, func=_clean_caches)
                
                # Task 3: Knowledge base self-reflection (every 12 hours)
                _run_task_if_due('run_self_reflection', now, hours=12, func=_run_self_reflection)
                
                # Task 4: Compress old embeddings (every 48 hours)
                _run_task_if_due('compress_embeddings', now, hours=48, func=_compress_embeddings)
                
                # Task 5: Optimize database (every 72 hours) 
                _run_task_if_due('optimize_database', now, hours=72, func=_optimize_database)
                
            except Exception as e:
                logging.error(f"Error running scheduled tasks: {str(e)}")
            finally:
                # Clean up the app context if we created one
                if context is not None:
                    context.__exit__(None, None, None)
        except Exception as e:
            logging.error(f"Error in maintenance worker: {str(e)}")
            
        # Sleep before checking again
        time.sleep(60 * 30)  # Check every 30 minutes

def _run_task_if_due(task_name: str, now: datetime, hours: int, func) -> bool:
    """Run a task if it's due to run."""
    last_run = _last_run_times.get(task_name)
    
    if last_run is None or now - last_run > timedelta(hours=hours):
        try:
            logging.info(f"Running maintenance task: {task_name}")
            func()
            _last_run_times[task_name] = now
            return True
        except Exception as e:
            logging.error(f"Error running maintenance task {task_name}: {str(e)}")
    
    return False

def _prune_knowledge_base():
    """Prune the knowledge base to keep it at a manageable size."""
    # Skip this task for now as it depends on external functionality
    logging.info("Knowledge base pruning skipped - needs further configuration")
    return

def _clean_caches():
    """Clean up all in-memory caches."""
    try:
        # We need to handle app context for database caches
        try:
            # Try to get a Flask app context directly
            from flask import current_app, has_app_context
            if has_app_context():
                from utils.cache_helper import clear_caches
                clear_caches()
                logging.info("Cleared all in-memory caches with existing app context")
                return
            
            # No current app context, try to create one
            try:
                # Try first import pattern
                from app import app
                with app.app_context():
                    from utils.cache_helper import clear_caches
                    clear_caches()
                    logging.info("Cleared all in-memory caches with new app context")
                    return
            except ImportError:
                # Try alternate import pattern
                try:
                    from main import app
                    with app.app_context():
                        from utils.cache_helper import clear_caches
                        clear_caches()
                        logging.info("Cleared all in-memory caches with alternate app context")
                        return
                except ImportError:
                    logging.warning("Could not import Flask app, falling back to file-based cache")
                    # Fall back to manually clearing file cache
                    import os
                    cache_dir = os.path.join(os.getcwd(), "cache")
                    if os.path.exists(cache_dir):
                        count = 0
                        for filename in os.listdir(cache_dir):
                            if filename.endswith(".json"):
                                os.remove(os.path.join(cache_dir, filename))
                                count += 1
                        logging.info(f"Cleared {count} file cache entries")
                    return
        except ImportError:
            # Flask not available, try to use cache_helper directly
            from utils.cache_helper import clear_caches
            clear_caches()
            logging.info("Cleared all in-memory caches without app context")
    except Exception as e:
        logging.error(f"Error in cache cleanup: {str(e)}")

def _run_self_reflection():
    """Run self-reflection to improve knowledge base quality."""
    # Skip this task for now as it depends on external functionality
    logging.info("Self-reflection skipped - needs further configuration")
    return

def _compress_embeddings():
    """Find and compress any uncompressed embeddings."""
    # Skip this task for now as it depends on specific model implementation
    logging.info("Embedding compression skipped - needs further configuration")
    return

def _optimize_database():
    """Run database optimization operations."""
    try:
        # We need a Flask app context to access the database
        from flask import has_app_context
        if not has_app_context():
            logging.info("Database optimization skipped - no application context available")
            return
            
        # Now we can safely import db
        try:
            from models import db
            from sqlalchemy import text
            
            # Check if db is initialized properly
            if not hasattr(db, 'engine') or db.engine is None:
                logging.info("Database optimization skipped - database not initialized")
                return
            
            # To properly run VACUUM, we need to run it outside a transaction
            try:
                # Commit any pending transactions
                db.session.commit()
                
                # Connect with autocommit mode
                connection = db.engine.connect()
                connection.execution_options(isolation_level="AUTOCOMMIT")
                
                # Run vacuum
                connection.execute(text("VACUUM ANALYZE"))
                logging.info("Database VACUUM ANALYZE completed")
                
                # Close the connection
                connection.close()
            except Exception as e:
                logging.error(f"Error running VACUUM: {str(e)}")
            
            # Additional PostgreSQL optimizations
            try:
                # Create a new connection for other operations
                with db.engine.connect() as conn:
                    # Update statistics
                    conn.execute(text("ANALYZE"))
                    
                    # Optimize specific tables that may have a lot of updates/deletes
                    # Get existing tables to avoid errors from non-existent tables
                    table_query = text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
                    existing_tables = [row[0] for row in conn.execute(table_query)]
                    
                    # Only reindex tables that exist
                    for table in ['knowledge_base']:
                        if table in existing_tables:
                            try:
                                conn.execute(text(f"REINDEX TABLE {table}"))
                            except Exception as e:
                                logging.warning(f"Could not reindex table {table}: {str(e)}")
                    
                    conn.commit()
                    
                logging.info("Database optimization tasks completed")
            except Exception as e:
                logging.error(f"Error optimizing database: {str(e)}")
        except ImportError:
            logging.warning("Database models not available")
    except Exception as e:
        logging.error(f"Error in database optimization: {str(e)}")

# Start the maintenance scheduler when the module is imported
start_maintenance_scheduler()