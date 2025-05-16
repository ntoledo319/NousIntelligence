"""
Batch Processing Helper
Provides functions to batch AI API requests to reduce costs and improve throughput.
Optimizes batching by dynamically adjusting batch sizes and timeouts.
"""

import logging
import time
from typing import List, Dict, Any, Callable, Optional, Tuple
import threading
import queue
import numpy as np
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)

# Constants
MAX_BATCH_SIZE = 50  # Increased from 20
MIN_BATCH_SIZE = 5   # Process at least this many at once if available
BATCH_WAIT_TIME = 0.5  # Reduced from 1.0 second to improve latency
MAX_QUEUE_SIZE = 1000  # Prevent unbounded queue growth
ADAPTIVE_TIMEOUT = True  # Dynamically adjust timeout based on queue size

# Performance metrics
_batch_stats = {
    'batches_processed': 0,
    'total_items_processed': 0,
    'avg_batch_size': 0,
    'total_processing_time': 0,
    'avg_processing_time': 0,
    'last_batch_time': 0
}

# Global batching queues for different types of operations
_embedding_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
_embedding_results = {}
_embedding_thread = None
_embedding_thread_running = False

# Batch completion callback queue
_completion_queue = queue.Queue()

# Lock for thread safety
_lock = threading.Lock()

def calculate_optimal_batch_size() -> int:
    """
    Dynamically calculate optimal batch size based on current load
    
    Returns:
        int: Optimal batch size between MIN_BATCH_SIZE and MAX_BATCH_SIZE
    """
    queue_size = _embedding_queue.qsize()
    
    # If queue is nearly empty, process small batches quickly
    if queue_size <= MIN_BATCH_SIZE:
        return MIN_BATCH_SIZE
    
    # If queue is very full, process maximum size batches
    if queue_size >= MAX_BATCH_SIZE * 2:
        return MAX_BATCH_SIZE
        
    # Otherwise scale batch size with queue size
    return min(max(queue_size // 2, MIN_BATCH_SIZE), MAX_BATCH_SIZE)

def calculate_wait_time() -> float:
    """
    Dynamically calculate wait time based on queue size
    
    Returns:
        float: Wait time in seconds
    """
    if not ADAPTIVE_TIMEOUT:
        return BATCH_WAIT_TIME
        
    queue_size = _embedding_queue.qsize()
    
    # If queue is large, reduce wait time to process faster
    if queue_size > MAX_BATCH_SIZE * 2:
        return 0.1  # Very short wait for large queues
    
    # If queue is moderate, use standard wait time
    if queue_size > MIN_BATCH_SIZE:
        return BATCH_WAIT_TIME
        
    # If queue is nearly empty, wait longer to collect items
    return 1.0  # Longer wait for small queues

def update_batch_stats(batch_size: int, processing_time: float) -> None:
    """
    Update batch processing statistics
    
    Args:
        batch_size: Size of the processed batch
        processing_time: Time taken to process the batch in seconds
    """
    with _lock:
        _batch_stats['batches_processed'] += 1
        _batch_stats['total_items_processed'] += batch_size
        _batch_stats['total_processing_time'] += processing_time
        _batch_stats['last_batch_time'] = processing_time
        
        # Recalculate averages
        if _batch_stats['batches_processed'] > 0:
            _batch_stats['avg_batch_size'] = _batch_stats['total_items_processed'] / _batch_stats['batches_processed']
            _batch_stats['avg_processing_time'] = _batch_stats['total_processing_time'] / _batch_stats['batches_processed']

def process_embeddings_batch():
    """Worker thread that processes embedding requests in batches"""
    global _embedding_thread_running
    
    try:
        while _embedding_thread_running:
            # Determine optimal batch size based on current load
            optimal_batch_size = calculate_optimal_batch_size()
            wait_time = calculate_wait_time()
            
            # Collect batch of up to optimal_batch_size items or wait wait_time seconds
            batch = []
            try:
                # Always get at least one item (blocking)
                item = _embedding_queue.get(block=True, timeout=wait_time)
                batch.append(item)
                
                # Try to get more items, up to batch size (non-blocking)
                for _ in range(optimal_batch_size - 1):
                    if not _embedding_queue.empty():
                        batch.append(_embedding_queue.get(block=False))
                    else:
                        break
            except queue.Empty:
                # No items in queue, continue loop
                continue
            
            # If we have items to process
            if batch:
                batch_size = len(batch)
                logger.info(f"Processing batch of {batch_size} embedding requests")
                start_time = time.time()
                
                # Extract texts and IDs
                texts = [item['text'] for item in batch]
                request_ids = [item['id'] for item in batch]
                
                # Get embeddings based on service preference
                try:
                    # Import here to avoid circular imports
                    from utils.models_config import get_model_for_task
                    
                    # Get the appropriate embedding model
                    provider, model = get_model_for_task("embedding")
                    
                    embeddings = process_embedding_batch(texts, provider, model)
                    
                    # Store results for each request
                    for i, request_id in enumerate(request_ids):
                        with _lock:
                            _embedding_results[request_id] = {
                                'embedding': embeddings[i],
                                'done': True,
                                'error': None
                            }
                            
                except Exception as e:
                    logger.error(f"Error processing embedding batch: {str(e)}")
                    # Store error for all requests in this batch
                    for request_id in request_ids:
                        with _lock:
                            _embedding_results[request_id] = {
                                'embedding': None,
                                'done': True,
                                'error': str(e)
                            }
                
                # Mark all items as processed
                for _ in range(batch_size):
                    _embedding_queue.task_done()
                
                # Update stats
                processing_time = time.time() - start_time
                update_batch_stats(batch_size, processing_time)
                
                # Log performance metrics periodically
                if _batch_stats['batches_processed'] % 10 == 0:
                    logger.info(f"Batch stats: avg_size={_batch_stats['avg_batch_size']:.1f}, "
                               f"avg_time={_batch_stats['avg_processing_time']:.3f}s")
    except Exception as e:
        logger.error(f"Embedding batch thread error: {str(e)}")
        _embedding_thread_running = False

def process_embedding_batch(texts: List[str], provider: str, model: str) -> List[np.ndarray]:
    """
    Process a batch of texts to get embeddings
    
    Args:
        texts: List of texts to embed
        provider: AI provider to use
        model: Model name to use
        
    Returns:
        List of embedding vectors (numpy arrays)
    """
    if provider == "huggingface":
        from utils.huggingface_helper import hf_batch_text_embeddings
        
        # Try batch processing if available
        try:
            embeddings = hf_batch_text_embeddings(texts, model)
            if embeddings:
                return embeddings
        except (ImportError, AttributeError):
            # Fall back to individual processing
            pass
            
        # Process one by one if batch processing failed or isn't available
        from utils.huggingface_helper import hf_text_embeddings
        embeddings = []
        for text in texts:
            embedding = hf_text_embeddings(text, model)
            # Convert to numpy array for consistent handling
            if embedding is not None:
                if isinstance(embedding, list):
                    embedding = np.array(embedding, dtype=np.float32)
                elif isinstance(embedding, float):
                    # Create a fallback embedding if we got a scalar
                    embedding = np.ones(384, dtype=np.float32) * embedding
            embeddings.append(embedding)
        return embeddings
            
    elif provider == "openrouter":
        from utils.knowledge_helper import get_embedding_via_openrouter
        
        # Process one by one (could be optimized if OpenRouter supports batching)
        embeddings = []
        for text in texts:
            embedding = get_embedding_via_openrouter(text)
            embeddings.append(embedding)
        return embeddings
            
    elif provider == "openai":
        from utils.knowledge_helper import get_embedding_for_text
        
        # Process one by one until we implement OpenAI batching
        embeddings = []
        for text in texts:
            embedding = get_embedding_for_text(text)
            embeddings.append(embedding)
        return embeddings
            
    else:  # Local fallback
        import hashlib
        
        # Generate deterministic fallback embeddings
        embeddings = []
        for text in texts:
            # Create a deterministic pseudo-embedding based on the text hash
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            # Use hash to seed a random generator for consistent results
            import random
            random.seed(hash_bytes)
            # Generate a pseudo-embedding of the correct dimension
            pseudo_embedding = np.array([
                random.uniform(-1, 1) for _ in range(384)
            ], dtype=np.float32)
            embeddings.append(pseudo_embedding)
        return embeddings

def start_batch_processing():
    """Start the background batch processing threads"""
    global _embedding_thread, _embedding_thread_running
    
    if _embedding_thread is None or not _embedding_thread.is_alive():
        _embedding_thread_running = True
        _embedding_thread = threading.Thread(target=process_embeddings_batch, daemon=True)
        _embedding_thread.start()
        logging.info("Started embedding batch processing thread")

def stop_batch_processing():
    """Stop the background batch processing threads"""
    global _embedding_thread_running
    _embedding_thread_running = False
    logging.info("Stopped embedding batch processing")

def get_embedding_batched(text, wait=True, timeout=10.0):
    """
    Get an embedding for text using batch processing for efficiency.
    
    Args:
        text (str): The text to embed
        wait (bool): Whether to wait for the result or return immediately
        timeout (float): Maximum time to wait for result in seconds
        
    Returns:
        numpy.ndarray or None: The embedding vector or None if wait=False
    """
    # Make sure batch processing is running
    start_batch_processing()
    
    # Generate a unique request ID
    import uuid
    request_id = str(uuid.uuid4())
    
    # Initialize result entry
    with _lock:
        _embedding_results[request_id] = {
            'embedding': None,
            'done': False,
            'error': None
        }
    
    # Add to processing queue
    _embedding_queue.put({
        'id': request_id,
        'text': text
    })
    
    # If not waiting, return immediately
    if not wait:
        return None
    
    # Wait for result
    start_time = time.time()
    while time.time() - start_time < timeout:
        with _lock:
            if _embedding_results[request_id]['done']:
                embedding = _embedding_results[request_id]['embedding']
                error = _embedding_results[request_id]['error']
                
                # Clean up
                del _embedding_results[request_id]
                
                if error:
                    logging.warning(f"Error in batched embedding: {error}")
                    return None
                    
                return embedding
                
        # Sleep briefly to avoid CPU spinning
        time.sleep(0.1)
    
    # Timeout reached
    logging.warning(f"Timeout waiting for embedding of text: {text[:50]}...")
    return None

# Initialize batch processing on module import
start_batch_processing()