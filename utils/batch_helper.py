"""
Batch Processing Helper
Provides functions to batch AI API requests to reduce costs.
"""

import logging
import time
from typing import List, Dict, Any, Callable, Optional
import threading
import queue
import numpy as np

# Global batching queues for different types of operations
_embedding_queue = queue.Queue()
_embedding_results = {}
_embedding_thread = None
_embedding_thread_running = False

# Lock for thread safety
_lock = threading.Lock()

def process_embeddings_batch():
    """Worker thread that processes embedding requests in batches"""
    global _embedding_thread_running
    
    try:
        while _embedding_thread_running:
            # Collect batch of up to 20 items or wait 1 second
            batch = []
            try:
                # Always get at least one item (blocking)
                item = _embedding_queue.get(block=True, timeout=1.0)
                batch.append(item)
                
                # Try to get more items, up to batch size (non-blocking)
                for _ in range(19):  # (20-1) more items
                    if not _embedding_queue.empty():
                        batch.append(_embedding_queue.get(block=False))
                    else:
                        break
            except queue.Empty:
                # No items in queue, continue loop
                continue
            
            # If we have items to process
            if batch:
                logging.info(f"Processing batch of {len(batch)} embedding requests")
                
                # Extract texts and IDs
                texts = [item['text'] for item in batch]
                request_ids = [item['id'] for item in batch]
                
                # Get embeddings based on service preference
                try:
                    # Import here to avoid circular imports
                    from utils.models_config import get_model_for_task
                    
                    # Get the appropriate embedding model
                    provider, model = get_model_for_task("embedding")
                    
                    if provider == "huggingface":
                        from utils.huggingface_helper import hf_text_embeddings
                        
                        # Process one by one since Hugging Face doesn't support batching directly
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
                            
                    elif provider == "openrouter":
                        from utils.knowledge_helper import get_embedding_via_openrouter
                        
                        # Process one by one (could be optimized if OpenRouter supports batching)
                        embeddings = []
                        for text in texts:
                            embedding = get_embedding_via_openrouter(text)
                            embeddings.append(embedding)
                            
                    elif provider == "openai":
                        from utils.knowledge_helper import get_embedding_for_text
                        
                        # Process one by one until we implement OpenAI batching
                        embeddings = []
                        for text in texts:
                            embedding = get_embedding_for_text(text)
                            embeddings.append(embedding)
                            
                    else:  # Local fallback
                        import hashlib
                        import numpy as np
                        
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
                    
                    # Store results for each request
                    for i, request_id in enumerate(request_ids):
                        with _lock:
                            _embedding_results[request_id] = {
                                'embedding': embeddings[i],
                                'done': True,
                                'error': None
                            }
                            
                except Exception as e:
                    logging.error(f"Error processing embedding batch: {str(e)}")
                    # Store error for all requests in this batch
                    for request_id in request_ids:
                        with _lock:
                            _embedding_results[request_id] = {
                                'embedding': None,
                                'done': True,
                                'error': str(e)
                            }
                
                # Mark all items as processed
                for _ in range(len(batch)):
                    _embedding_queue.task_done()
    except Exception as e:
        logging.error(f"Embedding batch thread error: {str(e)}")
        _embedding_thread_running = False

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