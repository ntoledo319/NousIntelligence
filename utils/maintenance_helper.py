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
    from app import app
    
    while _should_run:
        try:
            # Run with app context
            with app.app_context():
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
            logging.error(f"Error in maintenance worker: {str(e)}")
            
        # Sleep for a while before checking again
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
    from utils.knowledge_helper import prune_knowledge_base
    
    # Prune global knowledge
    result = prune_knowledge_base(user_id=None, max_entries=1000, min_relevance=0.2, run_async=False)
    logging.info(f"Pruned {result or 0} global knowledge entries")
    
    # Get list of active users
    from models import User
    users = User.query.filter_by(account_active=True).all()
    
    # Prune each user's knowledge
    for user in users:
        result = prune_knowledge_base(user_id=user.id, max_entries=500, min_relevance=0.3, run_async=False)
        logging.info(f"Pruned {result or 0} knowledge entries for user {user.id}")

def _clean_caches():
    """Clean up all in-memory caches."""
    from utils.cache_helper import clear_caches
    clear_caches()
    logging.info("Cleared all in-memory caches")

def _run_self_reflection():
    """Run self-reflection to improve knowledge base quality."""
    from utils.knowledge_helper import run_self_reflection
    
    # Run global self-reflection
    new_entries = run_self_reflection(user_id=None, max_prompts=3, run_async=False)
    logging.info(f"Added {len(new_entries) if new_entries else 0} new global knowledge entries via self-reflection")

def _compress_embeddings():
    """Find and compress any uncompressed embeddings."""
    import zlib
    import numpy as np
    from app import db
    from models import KnowledgeBase
    
    # Get all knowledge entries
    entries = KnowledgeBase.query.all()
    compressed_count = 0
    
    for entry in entries:
        try:
            # Check if it's already compressed
            try:
                zlib.decompress(entry.embedding)
                # If it gets here, it's already compressed
                continue
            except:
                # Not compressed, proceed with compression
                pass
                
            # Get the embedding as array
            embedding_array = entry.get_embedding_array()
            
            # Check if it's not empty
            if np.all(np.isclose(embedding_array, 0)):
                continue
                
            # Compress and save
            compressed = zlib.compress(embedding_array.astype(np.float16).tobytes(), level=6)
            entry.embedding = compressed
            compressed_count += 1
            
        except Exception as e:
            logging.error(f"Error compressing embedding for entry {entry.id}: {str(e)}")
    
    # Save changes
    if compressed_count > 0:
        db.session.commit()
        logging.info(f"Compressed {compressed_count} embeddings")

def _optimize_database():
    """Run database optimization operations."""
    from app import db
    from sqlalchemy import text
    
    # Run VACUUM to reclaim space and update statistics
    try:
        db.session.execute(text("VACUUM ANALYZE"))
        logging.info("Database VACUUM ANALYZE completed")
    except Exception as e:
        logging.error(f"Error running VACUUM: {str(e)}")
    
    # Additional PostgreSQL optimizations
    try:
        # Update statistics
        db.session.execute(text("ANALYZE"))
        
        # Optimize specific tables that may have a lot of updates/deletes
        for table in ['knowledge_base', 'command_log', 'google_tokens']:
            db.session.execute(text(f"REINDEX TABLE {table}"))
            
        logging.info("Database optimization tasks completed")
    except Exception as e:
        logging.error(f"Error optimizing database: {str(e)}")

# Start the maintenance scheduler when the module is imported
start_maintenance_scheduler()