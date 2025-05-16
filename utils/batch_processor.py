"""
@module batch_processor
@description Batch processing for external API requests to improve performance and reduce costs
@author AI Assistant
"""

import time
import asyncio
import logging
from typing import List, Dict, Any, Callable, Optional, TypeVar, Generic, Union, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logger
logger = logging.getLogger(__name__)

# Generic type for request and response
T = TypeVar('T')
R = TypeVar('R')

@dataclass
class BatchRequest(Generic[T, R]):
    """
    A request that will be processed in a batch
    
    Attributes:
        id: Unique identifier for this request
        data: The request data
        callback: Optional callback to be called when result is ready
        result: The result once processed (initially None)
        error: Error message if processing failed
        processed: Whether the request has been processed
        future: Future for this request when using async
    """
    id: str
    data: T
    callback: Optional[Callable[[R], None]] = None
    result: Optional[R] = None
    error: Optional[str] = None
    processed: bool = False
    future: Optional[asyncio.Future] = None

class BatchProcessor(Generic[T, R]):
    """
    Generic batch processor for efficiently handling multiple similar requests
    
    This processor collects individual requests over a time window and processes
    them together as a batch to reduce API calls and improve efficiency.
    """
    
    def __init__(self, 
                processor_func: Callable[[List[T]], List[R]],
                max_batch_size: int = 50,
                max_wait_time: float = 0.5,
                error_handler: Optional[Callable[[Exception, List[BatchRequest]], None]] = None):
        """
        Initialize the batch processor
        
        Args:
            processor_func: Function that processes a batch of requests
            max_batch_size: Maximum number of items to include in a batch
            max_wait_time: Maximum time to wait before processing a non-full batch (seconds)
            error_handler: Optional function to handle errors during batch processing
        """
        self.processor_func = processor_func
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self.error_handler = error_handler
        
        self.batch: List[BatchRequest[T, R]] = []
        self.lock = threading.RLock()
        self.batch_timer: Optional[threading.Timer] = None
        self.processing = False
        self.executor = ThreadPoolExecutor(max_workers=1)
        
        # For async support
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    def add_request(self, request_id: str, data: T, 
                   callback: Optional[Callable[[R], None]] = None) -> str:
        """
        Add a request to the current batch
        
        Args:
            request_id: Unique identifier for this request
            data: The request data
            callback: Optional callback for when result is ready
            
        Returns:
            The request ID
        """
        with self.lock:
            # Create the batch request
            batch_request = BatchRequest(id=request_id, data=data, callback=callback)
            
            # Add to batch
            self.batch.append(batch_request)
            
            # Start timer if this is the first request
            if len(self.batch) == 1:
                self._start_timer()
            
            # Process immediately if batch is full
            if len(self.batch) >= self.max_batch_size:
                self._cancel_timer()
                self._process_batch()
                
            return request_id
    
    async def add_request_async(self, request_id: str, data: T) -> R:
        """
        Add a request asynchronously and wait for the result
        
        Args:
            request_id: Unique identifier for this request
            data: The request data
            
        Returns:
            The result of processing the request
        """
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
            
        # Create a future for this request
        future = self.loop.create_future()
        
        # Add the request with the future
        with self.lock:
            batch_request = BatchRequest(
                id=request_id, 
                data=data, 
                future=future
            )
            self.batch.append(batch_request)
            
            # Start timer if this is the first request
            if len(self.batch) == 1:
                self._start_timer()
            
            # Process immediately if batch is full
            if len(self.batch) >= self.max_batch_size:
                self._cancel_timer()
                await self._process_batch_async()
        
        # Wait for the result
        return await future
    
    def get_result(self, request_id: str) -> Tuple[bool, Optional[R], Optional[str]]:
        """
        Get the result of a request by ID
        
        Args:
            request_id: ID of the request
            
        Returns:
            Tuple of (processed, result, error)
        """
        with self.lock:
            for request in self.batch:
                if request.id == request_id:
                    return (request.processed, request.result, request.error)
                    
        # Request not found
        return (False, None, "Request not found")
    
    def _start_timer(self) -> None:
        """Start the batch processing timer"""
        self.batch_timer = threading.Timer(self.max_wait_time, self._timer_callback)
        self.batch_timer.daemon = True
        self.batch_timer.start()
    
    def _cancel_timer(self) -> None:
        """Cancel the current timer if it exists"""
        if self.batch_timer:
            self.batch_timer.cancel()
            self.batch_timer = None
    
    def _timer_callback(self) -> None:
        """Called when the timer expires"""
        with self.lock:
            if not self.processing and self.batch:
                self._process_batch()
    
    def _process_batch(self) -> None:
        """Process the current batch of requests"""
        with self.lock:
            if self.processing or not self.batch:
                return
                
            self.processing = True
            current_batch = self.batch.copy()
            self.batch = []
            
        # Process the batch in a background thread
        self.executor.submit(self._do_process_batch, current_batch)
    
    async def _process_batch_async(self) -> None:
        """Process the current batch of requests asynchronously"""
        with self.lock:
            if self.processing or not self.batch:
                return
                
            self.processing = True
            current_batch = self.batch.copy()
            self.batch = []
        
        # Process the batch
        try:
            # Get just the data from each request
            batch_data = [request.data for request in current_batch]
            
            # Process the batch
            results = await asyncio.to_thread(self.processor_func, batch_data)
            
            # Match results to requests
            for i, request in enumerate(current_batch):
                if i < len(results):
                    request.result = results[i]
                    request.processed = True
                    
                    # Set the future result if this is an async request
                    if request.future and not request.future.done():
                        request.future.set_result(results[i])
                else:
                    request.error = "No result returned for this request"
                    request.processed = True
                    
                    # Set the future exception if this is an async request
                    if request.future and not request.future.done():
                        request.future.set_exception(Exception(request.error))
        except Exception as e:
            logger.exception(f"Error processing batch: {str(e)}")
            
            # Handle the error for each request
            for request in current_batch:
                request.error = str(e)
                request.processed = True
                
                # Set the future exception if this is an async request
                if request.future and not request.future.done():
                    request.future.set_exception(e)
            
            # Call error handler if provided
            if self.error_handler:
                try:
                    self.error_handler(e, current_batch)
                except Exception as handler_error:
                    logger.exception(f"Error in batch error handler: {str(handler_error)}")
        finally:
            self.processing = False
    
    def _do_process_batch(self, batch: List[BatchRequest[T, R]]) -> None:
        """
        Actually process a batch of requests
        
        Args:
            batch: List of batch requests to process
        """
        try:
            # Get just the data from each request
            batch_data = [request.data for request in batch]
            
            # Process the batch
            results = self.processor_func(batch_data)
            
            # Match results to requests
            for i, request in enumerate(batch):
                if i < len(results):
                    request.result = results[i]
                    request.processed = True
                    
                    # Call the callback if provided
                    if request.callback:
                        try:
                            request.callback(results[i])
                        except Exception as callback_error:
                            logger.exception(f"Error in callback for request {request.id}: {str(callback_error)}")
                else:
                    request.error = "No result returned for this request"
                    request.processed = True
        except Exception as e:
            logger.exception(f"Error processing batch: {str(e)}")
            
            # Handle the error for each request
            for request in batch:
                request.error = str(e)
                request.processed = True
            
            # Call error handler if provided
            if self.error_handler:
                try:
                    self.error_handler(e, batch)
                except Exception as handler_error:
                    logger.exception(f"Error in batch error handler: {str(handler_error)}")
        finally:
            self.processing = False
            
            # Check if we need to process more batches
            with self.lock:
                if self.batch:
                    self._start_timer()

class EmbeddingBatchProcessor(BatchProcessor[str, List[float]]):
    """
    Specialized batch processor for text embeddings
    
    This processor batches embedding requests to reduce API calls
    and improve throughput when generating embeddings.
    """
    
    def __init__(self, 
                embedding_func: Callable[[List[str]], List[List[float]]],
                max_batch_size: int = 32,
                max_wait_time: float = 0.5):
        """
        Initialize the embedding batch processor
        
        Args:
            embedding_func: Function that generates embeddings for a batch of texts
            max_batch_size: Maximum batch size (defaults to 32 for most embedding APIs)
            max_wait_time: Maximum time to wait before processing (seconds)
        """
        super().__init__(
            processor_func=embedding_func,
            max_batch_size=max_batch_size,
            max_wait_time=max_wait_time
        )

class CompletionBatchProcessor(BatchProcessor[Dict[str, Any], Dict[str, Any]]):
    """
    Specialized batch processor for text completions
    
    This processor batches similar completion requests to reduce API calls
    and improve throughput.
    """
    
    def __init__(self, 
                completion_func: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
                max_batch_size: int = 20,
                max_wait_time: float = 0.8):
        """
        Initialize the completion batch processor
        
        Args:
            completion_func: Function that generates completions for a batch of prompts
            max_batch_size: Maximum batch size
            max_wait_time: Maximum time to wait before processing (seconds)
        """
        super().__init__(
            processor_func=completion_func,
            max_batch_size=max_batch_size,
            max_wait_time=max_wait_time
        )

# Examples of how to use the batch processors

def example_embedding_batch_processor():
    """Example of using the embedding batch processor"""
    import uuid
    import numpy as np
    
    # Define a function that processes a batch of embedding requests
    def process_embeddings(texts: List[str]) -> List[List[float]]:
        # In a real application, this would call an embedding API
        # Here we just create random embeddings for demonstration
        logger.info(f"Processing batch of {len(texts)} embeddings")
        time.sleep(0.5)  # Simulate API call
        return [np.random.randn(384).tolist() for _ in texts]
    
    # Create the batch processor
    embedding_processor = EmbeddingBatchProcessor(
        embedding_func=process_embeddings,
        max_batch_size=10,
        max_wait_time=1.0
    )
    
    # Add some requests
    for i in range(25):
        text = f"This is sample text {i} for embedding"
        request_id = str(uuid.uuid4())
        
        def make_callback(idx):
            return lambda result: logger.info(f"Got embedding for text {idx} with dimension {len(result)}")
        
        embedding_processor.add_request(
            request_id=request_id,
            data=text,
            callback=make_callback(i)
        )
    
    # Wait for all requests to be processed
    time.sleep(3)

async def example_async_embedding_batch_processor():
    """Example of using the embedding batch processor asynchronously"""
    import uuid
    import numpy as np
    
    # Define a function that processes a batch of embedding requests
    def process_embeddings(texts: List[str]) -> List[List[float]]:
        # In a real application, this would call an embedding API
        # Here we just create random embeddings for demonstration
        logger.info(f"Processing batch of {len(texts)} embeddings")
        time.sleep(0.5)  # Simulate API call
        return [np.random.randn(384).tolist() for _ in texts]
    
    # Create the batch processor
    embedding_processor = EmbeddingBatchProcessor(
        embedding_func=process_embeddings,
        max_batch_size=10,
        max_wait_time=1.0
    )
    
    # Add some requests asynchronously
    tasks = []
    for i in range(25):
        text = f"This is sample text {i} for embedding"
        request_id = str(uuid.uuid4())
        task = asyncio.create_task(
            embedding_processor.add_request_async(request_id, text)
        )
        tasks.append(task)
    
    # Wait for all results
    results = await asyncio.gather(*tasks)
    for i, embedding in enumerate(results):
        logger.info(f"Got embedding {i} with dimension {len(embedding)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Synchronous example
    example_embedding_batch_processor()
    
    # Async example
    asyncio.run(example_async_embedding_batch_processor()) 