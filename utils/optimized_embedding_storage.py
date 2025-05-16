"""
@module optimized_embedding_storage
@description Efficient embedding storage with compression and optimized retrieval
@author AI Assistant
"""

import os
import time
import numpy as np
import json
import logging
import zlib
import pickle
import threading
import sqlite3
from typing import List, Dict, Any, Tuple, Optional, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DIMENSION = 384  # Default embedding dimension
SQLITE_VECTOR_EXTENSION = True  # Whether to use SQLite vector extension (if available)
QUANTIZATION_ENABLED = True  # Whether to enable embedding quantization
PCA_REDUCTION_ENABLED = False  # Whether to enable PCA dimension reduction
COMPRESSION_ENABLED = True  # Whether to enable embedding compression
DEFAULT_CACHE_DIR = os.path.join(os.getcwd(), "cache", "embeddings")

# Create cache directory if it doesn't exist
os.makedirs(DEFAULT_CACHE_DIR, exist_ok=True)

@dataclass
class EmbeddingMetadata:
    """
    Metadata for stored embeddings
    
    Attributes:
        id: Unique identifier for this embedding
        text: Original text that was embedded
        model: Model used to generate the embedding
        created_at: Timestamp when the embedding was created
        dimension: Dimension of the original embedding
        tags: Optional tags for categorization
        compressed: Whether the embedding is compressed
        quantized: Whether the embedding is quantized
        reduced: Whether dimension reduction was applied
        extra: Additional metadata
    """
    id: str
    text: str
    model: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    dimension: int = DEFAULT_DIMENSION
    tags: List[str] = field(default_factory=list)
    compressed: bool = False
    quantized: bool = False
    reduced: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

class EmbeddingCompressor:
    """Compressor for efficient embedding storage"""
    
    @staticmethod
    def compress(embedding: List[float], level: int = 5) -> bytes:
        """
        Compress an embedding vector
        
        Args:
            embedding: The embedding vector to compress
            level: Compression level (1-9)
            
        Returns:
            Compressed embedding as bytes
        """
        # Convert to bytes
        embedding_bytes = pickle.dumps(embedding)
        
        # Compress with zlib
        compressed = zlib.compress(embedding_bytes, level=level)
        
        return compressed
    
    @staticmethod
    def decompress(compressed_data: bytes) -> List[float]:
        """
        Decompress an embedding vector
        
        Args:
            compressed_data: Compressed embedding bytes
            
        Returns:
            Decompressed embedding vector
        """
        # Decompress with zlib
        decompressed = zlib.decompress(compressed_data)
        
        # Convert back to list
        embedding = pickle.loads(decompressed)
        
        return embedding

class EmbeddingQuantizer:
    """Quantizer for reduced-precision embedding storage"""
    
    @staticmethod
    def quantize_to_int8(embedding: List[float]) -> bytes:
        """
        Quantize a floating-point embedding to int8
        
        Args:
            embedding: Original floating-point embedding
            
        Returns:
            Quantized embedding as bytes and scale factor
        """
        # Convert to numpy array
        embedding_array = np.array(embedding, dtype=np.float32)
        
        # Find min and max for scaling
        min_val = embedding_array.min()
        max_val = embedding_array.max()
        
        # Compute scale factor and zero point
        scale = (max_val - min_val) / 255.0 if max_val > min_val else 1.0
        zero_point = -min_val / scale if scale > 0 else 0
        
        # Quantize to int8
        quantized = np.clip(np.round(embedding_array / scale + zero_point), 0, 255).astype(np.uint8)
        
        # Return quantized data, scale, and zero point
        return quantized.tobytes(), scale, min_val
    
    @staticmethod
    def dequantize_from_int8(quantized_data: bytes, scale: float, min_val: float, dimension: int) -> List[float]:
        """
        Dequantize an int8 embedding back to float
        
        Args:
            quantized_data: Quantized embedding bytes
            scale: Scale factor used during quantization
            min_val: Minimum value used during quantization
            dimension: Embedding dimension
            
        Returns:
            Dequantized embedding as list of floats
        """
        # Convert bytes to numpy array
        quantized = np.frombuffer(quantized_data, dtype=np.uint8)
        
        # Dequantize
        dequantized = (quantized.astype(np.float32) * scale) + min_val
        
        # Ensure correct dimension
        dequantized = dequantized[:dimension]
        
        return dequantized.tolist()

class EmbeddingDimensionReducer:
    """Dimension reducer for more efficient embedding storage"""
    
    def __init__(self, target_dimensions: int = 128):
        """
        Initialize the dimension reducer
        
        Args:
            target_dimensions: Target number of dimensions
        """
        self.target_dimensions = target_dimensions
        self.pca = None
        self.is_fitted = False
        self.fit_lock = threading.Lock()
    
    def fit(self, embeddings: List[List[float]]) -> None:
        """
        Fit PCA on a set of embeddings
        
        Args:
            embeddings: List of embedding vectors
        """
        with self.fit_lock:
            if self.is_fitted:
                return
                
            try:
                from sklearn.decomposition import PCA
                
                # Convert to numpy array
                embeddings_array = np.array(embeddings)
                
                # Ensure we don't reduce to more dimensions than we have
                n_components = min(self.target_dimensions, embeddings_array.shape[1], embeddings_array.shape[0])
                
                # Create and fit PCA
                self.pca = PCA(n_components=n_components)
                self.pca.fit(embeddings_array)
                
                self.is_fitted = True
                logger.info(f"PCA fitted for embedding reduction to {n_components} dimensions")
            except Exception as e:
                logger.error(f"Error fitting PCA for dimension reduction: {str(e)}")
    
    def transform(self, embedding: List[float]) -> List[float]:
        """
        Reduce dimensions of an embedding
        
        Args:
            embedding: Original embedding vector
            
        Returns:
            Reduced embedding vector
        """
        if not self.is_fitted or self.pca is None:
            logger.warning("PCA not fitted, returning original embedding")
            return embedding
            
        try:
            # Convert to numpy array with correct shape
            embedding_array = np.array(embedding).reshape(1, -1)
            
            # Transform
            reduced = self.pca.transform(embedding_array)
            
            # Return as list
            return reduced[0].tolist()
        except Exception as e:
            logger.error(f"Error reducing embedding dimensions: {str(e)}")
            return embedding
    
    def inverse_transform(self, reduced_embedding: List[float]) -> List[float]:
        """
        Restore original dimensions of a reduced embedding
        
        Args:
            reduced_embedding: Reduced embedding vector
            
        Returns:
            Reconstructed embedding vector
        """
        if not self.is_fitted or self.pca is None:
            logger.warning("PCA not fitted, returning original embedding")
            return reduced_embedding
            
        try:
            # Convert to numpy array with correct shape
            reduced_array = np.array(reduced_embedding).reshape(1, -1)
            
            # Inverse transform
            restored = self.pca.inverse_transform(reduced_array)
            
            # Return as list
            return restored[0].tolist()
        except Exception as e:
            logger.error(f"Error restoring embedding dimensions: {str(e)}")
            return reduced_embedding

class OptimizedEmbeddingStorage:
    """
    Optimized storage for embedding vectors with efficient formats and compression
    
    This class provides:
    - Compressed storage for embedding vectors
    - Quantization for reduced memory footprint
    - Optional dimension reduction for even more compact storage
    - Fast retrieval and similarity search
    - Metadata storage and search capabilities
    """
    
    def __init__(self, 
                database_path: Optional[str] = None,
                cache_dir: Optional[str] = None,
                compression_enabled: bool = COMPRESSION_ENABLED,
                quantization_enabled: bool = QUANTIZATION_ENABLED,
                dimension_reduction_enabled: bool = PCA_REDUCTION_ENABLED,
                target_dimensions: int = 128):
        """
        Initialize the optimized embedding storage
        
        Args:
            database_path: Path to SQLite database file (memory if None)
            cache_dir: Directory for file-based cache
            compression_enabled: Whether to enable compression
            quantization_enabled: Whether to enable quantization
            dimension_reduction_enabled: Whether to enable dimension reduction
            target_dimensions: Target dimensions if reduction enabled
        """
        # Settings
        self.compression_enabled = compression_enabled
        self.quantization_enabled = quantization_enabled
        self.dimension_reduction_enabled = dimension_reduction_enabled
        
        # Components
        self.compressor = EmbeddingCompressor()
        self.quantizer = EmbeddingQuantizer()
        self.dimension_reducer = EmbeddingDimensionReducer(target_dimensions=target_dimensions)
        
        # Storage paths
        self.database_path = database_path or ":memory:"
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        
        # Initialize database
        self._init_database()
        
        # Initialize directory storage
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info(f"Optimized embedding storage initialized: "
                   f"compression={self.compression_enabled}, "
                   f"quantization={self.quantization_enabled}, "
                   f"dimension_reduction={self.dimension_reduction_enabled}")
    
    def _init_database(self) -> None:
        """Initialize the SQLite database for embeddings storage"""
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            # Create embeddings metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS embeddings (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    tags TEXT,
                    compressed BOOLEAN NOT NULL,
                    quantized BOOLEAN NOT NULL,
                    reduced BOOLEAN NOT NULL,
                    scale REAL,
                    min_val REAL,
                    extra TEXT,
                    embedding BLOB
                )
            ''')
            
            # Create index on model
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model)')
            
            # Create index on created_at
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_embeddings_created_at ON embeddings(created_at)')
            
            # Create index on tags (if supported)
            try:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_embeddings_tags ON embeddings(tags)')
            except sqlite3.OperationalError:
                pass  # SQLite version might not support indexing TEXT columns
            
            # Enable vector extension if available and supported
            if SQLITE_VECTOR_EXTENSION:
                try:
                    cursor.execute('SELECT sqlite_version()')
                    version = cursor.fetchone()[0]
                    
                    if int(version.split('.')[0]) >= 3:
                        cursor.execute('SELECT load_extension("vector0")')
                        logger.info("SQLite vector extension loaded")
                except Exception as e:
                    logger.warning(f"Failed to load SQLite vector extension: {str(e)}")
            
            conn.commit()
            logger.info("Embedding database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def store(self, 
             text: str, 
             embedding: List[float], 
             model: str, 
             tags: Optional[List[str]] = None, 
             extra: Optional[Dict[str, Any]] = None) -> str:
        """
        Store an embedding with optimized format
        
        Args:
            text: Original text
            embedding: Embedding vector
            model: Model used to generate embedding
            tags: Optional tags for categorization
            extra: Additional metadata
            
        Returns:
            Unique ID for the stored embedding
        """
        # Generate unique ID
        embedding_id = str(uuid.uuid4())
        
        # Initialize metadata
        metadata = EmbeddingMetadata(
            id=embedding_id,
            text=text,
            model=model,
            dimension=len(embedding),
            tags=tags or [],
            extra=extra or {}
        )
        
        # Store original dimension for later restoration
        original_dimension = len(embedding)
        
        # Process the embedding with selected optimizations
        processed_embedding, scale, min_val = self._process_embedding(embedding)
        
        # Store in database
        self._store_in_database(metadata, processed_embedding, scale, min_val)
        
        # Store in file cache
        self._store_in_file(metadata, processed_embedding, scale, min_val)
        
        return embedding_id
    
    def _process_embedding(self, embedding: List[float]) -> Tuple[bytes, Optional[float], Optional[float]]:
        """
        Process an embedding with the selected optimizations
        
        Args:
            embedding: Original embedding vector
            
        Returns:
            Tuple of (processed_embedding_bytes, scale_factor, min_val)
        """
        processed = embedding
        scale = None
        min_val = None
        
        # Dimension reduction (if enabled)
        if self.dimension_reduction_enabled and hasattr(self.dimension_reducer, 'transform'):
            processed = self.dimension_reducer.transform(processed)
            metadata_updated = True
        
        # Quantization (if enabled)
        if self.quantization_enabled:
            processed_bytes, scale, min_val = self.quantizer.quantize_to_int8(processed)
        else:
            # Compression only (if enabled)
            if self.compression_enabled:
                processed_bytes = self.compressor.compress(processed)
            else:
                processed_bytes = pickle.dumps(processed)
        
        return processed_bytes, scale, min_val
    
    def _store_in_database(self, 
                          metadata: EmbeddingMetadata, 
                          embedding_data: bytes,
                          scale: Optional[float], 
                          min_val: Optional[float]) -> None:
        """
        Store embedding in the database
        
        Args:
            metadata: Embedding metadata
            embedding_data: Processed embedding data
            scale: Scale factor for quantization (if used)
            min_val: Minimum value for quantization (if used)
        """
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            # Update metadata flags
            metadata.compressed = self.compression_enabled
            metadata.quantized = self.quantization_enabled
            metadata.reduced = self.dimension_reduction_enabled
            
            # Store in database
            cursor.execute('''
                INSERT INTO embeddings 
                (id, text, model, created_at, dimension, tags, compressed, quantized, reduced, scale, min_val, extra, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.id,
                metadata.text,
                metadata.model,
                metadata.created_at.isoformat(),
                metadata.dimension,
                json.dumps(metadata.tags),
                metadata.compressed,
                metadata.quantized,
                metadata.reduced,
                scale,
                min_val,
                json.dumps(metadata.extra),
                embedding_data
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing embedding in database: {str(e)}")
            raise
        finally:
            conn.close()
    
    def _store_in_file(self, 
                      metadata: EmbeddingMetadata, 
                      embedding_data: bytes,
                      scale: Optional[float], 
                      min_val: Optional[float]) -> None:
        """
        Store embedding in file cache
        
        Args:
            metadata: Embedding metadata
            embedding_data: Processed embedding data
            scale: Scale factor for quantization (if used)
            min_val: Minimum value for quantization (if used)
        """
        try:
            # Create model-specific directory
            model_dir = os.path.join(self.cache_dir, metadata.model)
            os.makedirs(model_dir, exist_ok=True)
            
            # Define file paths
            metadata_path = os.path.join(model_dir, f"{metadata.id}.json")
            embedding_path = os.path.join(model_dir, f"{metadata.id}.bin")
            
            # Save metadata
            with open(metadata_path, 'w') as f:
                json_data = {
                    "id": metadata.id,
                    "text": metadata.text,
                    "model": metadata.model,
                    "created_at": metadata.created_at.isoformat(),
                    "dimension": metadata.dimension,
                    "tags": metadata.tags,
                    "compressed": metadata.compressed,
                    "quantized": metadata.quantized,
                    "reduced": metadata.reduced,
                    "scale": scale,
                    "min_val": min_val,
                    "extra": metadata.extra
                }
                json.dump(json_data, f)
            
            # Save embedding
            with open(embedding_path, 'wb') as f:
                f.write(embedding_data)
                
        except Exception as e:
            logger.error(f"Error storing embedding in file: {str(e)}")
            # Continue execution - database is primary storage
    
    def get(self, embedding_id: str) -> Tuple[Optional[EmbeddingMetadata], Optional[List[float]]]:
        """
        Retrieve an embedding by ID
        
        Args:
            embedding_id: ID of the embedding to retrieve
            
        Returns:
            Tuple of (metadata, embedding) or (None, None) if not found
        """
        # Try to get from database
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM embeddings WHERE id = ?
            ''', (embedding_id,))
            
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Embedding with ID {embedding_id} not found")
                return None, None
                
            # Parse metadata
            metadata = EmbeddingMetadata(
                id=row['id'],
                text=row['text'],
                model=row['model'],
                created_at=datetime.fromisoformat(row['created_at']),
                dimension=row['dimension'],
                tags=json.loads(row['tags']),
                compressed=bool(row['compressed']),
                quantized=bool(row['quantized']),
                reduced=bool(row['reduced']),
                extra=json.loads(row['extra'])
            )
            
            # Get embedding data
            embedding_data = row['embedding']
            
            # Restore embedding
            embedding = self._restore_embedding(
                embedding_data,
                row['scale'],
                row['min_val'],
                row['dimension'],
                bool(row['compressed']),
                bool(row['quantized']),
                bool(row['reduced'])
            )
            
            return metadata, embedding
            
        except Exception as e:
            logger.error(f"Error retrieving embedding from database: {str(e)}")
            
            # Try to get from file as fallback
            return self._get_from_file(embedding_id)
        finally:
            conn.close()
    
    def _get_from_file(self, embedding_id: str) -> Tuple[Optional[EmbeddingMetadata], Optional[List[float]]]:
        """
        Retrieve an embedding from file cache
        
        Args:
            embedding_id: ID of the embedding to retrieve
            
        Returns:
            Tuple of (metadata, embedding) or (None, None) if not found
        """
        try:
            # Search for the file in all model directories
            for model_dir in os.listdir(self.cache_dir):
                model_path = os.path.join(self.cache_dir, model_dir)
                
                if not os.path.isdir(model_path):
                    continue
                    
                metadata_path = os.path.join(model_path, f"{embedding_id}.json")
                embedding_path = os.path.join(model_path, f"{embedding_id}.bin")
                
                if os.path.exists(metadata_path) and os.path.exists(embedding_path):
                    # Load metadata
                    with open(metadata_path, 'r') as f:
                        metadata_dict = json.load(f)
                    
                    # Load embedding
                    with open(embedding_path, 'rb') as f:
                        embedding_data = f.read()
                    
                    # Create metadata object
                    metadata = EmbeddingMetadata(
                        id=metadata_dict['id'],
                        text=metadata_dict['text'],
                        model=metadata_dict['model'],
                        created_at=datetime.fromisoformat(metadata_dict['created_at']),
                        dimension=metadata_dict['dimension'],
                        tags=metadata_dict['tags'],
                        compressed=metadata_dict['compressed'],
                        quantized=metadata_dict['quantized'],
                        reduced=metadata_dict['reduced'],
                        extra=metadata_dict['extra']
                    )
                    
                    # Restore embedding
                    embedding = self._restore_embedding(
                        embedding_data,
                        metadata_dict.get('scale'),
                        metadata_dict.get('min_val'),
                        metadata_dict['dimension'],
                        metadata_dict['compressed'],
                        metadata_dict['quantized'],
                        metadata_dict['reduced']
                    )
                    
                    return metadata, embedding
            
            # Not found
            logger.warning(f"Embedding with ID {embedding_id} not found in file cache")
            return None, None
            
        except Exception as e:
            logger.error(f"Error retrieving embedding from file: {str(e)}")
            return None, None
    
    def _restore_embedding(self, 
                          embedding_data: bytes,
                          scale: Optional[float],
                          min_val: Optional[float],
                          dimension: int,
                          compressed: bool,
                          quantized: bool,
                          reduced: bool) -> List[float]:
        """
        Restore an embedding from its optimized format
        
        Args:
            embedding_data: Processed embedding data
            scale: Scale factor for quantization (if used)
            min_val: Minimum value for quantization (if used)
            dimension: Original embedding dimension
            compressed: Whether the embedding is compressed
            quantized: Whether the embedding is quantized
            reduced: Whether dimension reduction was applied
            
        Returns:
            Restored embedding vector
        """
        # Dequantize if quantized
        if quantized:
            embedding = self.quantizer.dequantize_from_int8(embedding_data, scale, min_val, dimension)
        else:
            # Decompress if compressed
            if compressed:
                embedding = self.compressor.decompress(embedding_data)
            else:
                embedding = pickle.loads(embedding_data)
        
        # Restore dimensions if reduced
        if reduced and hasattr(self.dimension_reducer, 'inverse_transform'):
            embedding = self.dimension_reducer.inverse_transform(embedding)
            
        return embedding
    
    def search(self, 
              query_embedding: List[float], 
              top_k: int = 10,
              model: Optional[str] = None,
              tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            model: Filter by model name
            tags: Filter by tags
            
        Returns:
            List of search results with similarity scores
        """
        # Prepare query embedding for comparison - handle optimizations
        if self.dimension_reduction_enabled and hasattr(self.dimension_reducer, 'transform'):
            query_embedding = self.dimension_reducer.transform(query_embedding)
        
        # Get all embeddings from database
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM embeddings"
            params = []
            
            filters = []
            if model:
                filters.append("model = ?")
                params.append(model)
            
            if tags:
                # SQLite JSON filtering is limited, so we'll post-filter tags
                pass
                
            if filters:
                query += " WHERE " + " AND ".join(filters)
                
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            
            # Calculate similarity for each embedding
            results = []
            
            for row in rows:
                # Skip if tag filtering is active and not matching
                if tags:
                    row_tags = json.loads(row['tags'])
                    if not any(tag in row_tags for tag in tags):
                        continue
                
                # Get embedding data
                embedding_data = row['embedding']
                
                # Restore embedding
                embedding = self._restore_embedding(
                    embedding_data,
                    row['scale'],
                    row['min_val'],
                    row['dimension'],
                    bool(row['compressed']),
                    bool(row['quantized']),
                    bool(row['reduced'])
                )
                
                # Calculate similarity
                similarity = self._calculate_similarity(query_embedding, embedding)
                
                # Add to results
                results.append({
                    "id": row['id'],
                    "text": row['text'],
                    "model": row['model'],
                    "similarity": similarity,
                    "tags": json.loads(row['tags']),
                    "created_at": row['created_at']
                })
            
            # Sort by similarity (highest first)
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top-k
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching embeddings: {str(e)}")
            return []
        finally:
            conn.close()
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Handle dimension mismatch
        min_dim = min(len(vec1), len(vec2))
        vec1 = vec1[:min_dim]
        vec2 = vec2[:min_dim]
        
        # Calculate cosine similarity
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def delete(self, embedding_id: str) -> bool:
        """
        Delete an embedding
        
        Args:
            embedding_id: ID of the embedding to delete
            
        Returns:
            True if deleted, False otherwise
        """
        # Delete from database
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            # Get the model before deleting
            cursor.execute("SELECT model FROM embeddings WHERE id = ?", (embedding_id,))
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Embedding with ID {embedding_id} not found for deletion")
                return False
                
            model = row['model']
            
            # Delete from database
            cursor.execute("DELETE FROM embeddings WHERE id = ?", (embedding_id,))
            conn.commit()
            
            # Also delete from file cache
            self._delete_from_file(embedding_id, model)
            
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting embedding from database: {str(e)}")
            return False
        finally:
            conn.close()
    
    def _delete_from_file(self, embedding_id: str, model: str) -> None:
        """
        Delete an embedding from file cache
        
        Args:
            embedding_id: ID of the embedding to delete
            model: Model name (for directory path)
        """
        try:
            model_dir = os.path.join(self.cache_dir, model)
            
            metadata_path = os.path.join(model_dir, f"{embedding_id}.json")
            embedding_path = os.path.join(model_dir, f"{embedding_id}.bin")
            
            # Delete files if they exist
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                
            if os.path.exists(embedding_path):
                os.remove(embedding_path)
                
        except Exception as e:
            logger.error(f"Error deleting embedding from file: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear the file cache but keep the database"""
        try:
            for model_dir in os.listdir(self.cache_dir):
                model_path = os.path.join(self.cache_dir, model_dir)
                
                if not os.path.isdir(model_path):
                    continue
                    
                for file_name in os.listdir(model_path):
                    file_path = os.path.join(model_path, file_name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        
            logger.info("Embedding file cache cleared")
        except Exception as e:
            logger.error(f"Error clearing embedding cache: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dictionary with statistics
        """
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            # Count embeddings
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            total_count = cursor.fetchone()[0]
            
            # Count by model
            cursor.execute("SELECT model, COUNT(*) FROM embeddings GROUP BY model")
            model_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Count by compression/quantization
            cursor.execute("SELECT COUNT(*) FROM embeddings WHERE compressed = 1")
            compressed_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM embeddings WHERE quantized = 1")
            quantized_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM embeddings WHERE reduced = 1")
            reduced_count = cursor.fetchone()[0]
            
            # Get average text length
            cursor.execute("SELECT AVG(LENGTH(text)) FROM embeddings")
            avg_text_length = cursor.fetchone()[0] or 0
            
            # Size estimation (rough approximation)
            cursor.execute("SELECT SUM(LENGTH(embedding)) FROM embeddings")
            total_bytes = cursor.fetchone()[0] or 0
            
            # Calculate storage efficiency
            if total_count > 0:
                avg_bytes_per_embedding = total_bytes / total_count
            else:
                avg_bytes_per_embedding = 0
            
            return {
                "total_embeddings": total_count,
                "by_model": model_counts,
                "compressed_count": compressed_count,
                "quantized_count": quantized_count,
                "reduced_count": reduced_count,
                "avg_text_length": round(avg_text_length, 2),
                "total_storage_bytes": total_bytes,
                "avg_bytes_per_embedding": round(avg_bytes_per_embedding, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {"error": str(e)}
        finally:
            conn.close()
    
    def optimize_storage(self) -> Dict[str, Any]:
        """
        Optimize existing storage for better efficiency
        
        This applies the current optimization settings to all embeddings
        
        Returns:
            Dictionary with optimization statistics
        """
        conn = self._get_db_connection()
        
        try:
            cursor = conn.cursor()
            
            # Get all embeddings that don't have the current optimization settings
            query = "SELECT * FROM embeddings WHERE "
            conditions = []
            
            if self.compression_enabled:
                conditions.append("compressed = 0")
            if self.quantization_enabled:
                conditions.append("quantized = 0")
            if self.dimension_reduction_enabled:
                conditions.append("reduced = 0")
                
            if not conditions:
                logger.info("No optimization needed - all settings already applied")
                return {"optimized_count": 0, "total_embeddings": 0}
                
            query += " OR ".join(conditions)
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            optimized_count = 0
            
            for row in rows:
                try:
                    # Restore original embedding
                    embedding_data = row['embedding']
                    embedding = self._restore_embedding(
                        embedding_data,
                        row['scale'],
                        row['min_val'],
                        row['dimension'],
                        bool(row['compressed']),
                        bool(row['quantized']),
                        bool(row['reduced'])
                    )
                    
                    # Process with current settings
                    processed_data, scale, min_val = self._process_embedding(embedding)
                    
                    # Update metadata
                    metadata = EmbeddingMetadata(
                        id=row['id'],
                        text=row['text'],
                        model=row['model'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        dimension=row['dimension'],
                        tags=json.loads(row['tags']),
                        compressed=self.compression_enabled,
                        quantized=self.quantization_enabled,
                        reduced=self.dimension_reduction_enabled,
                        extra=json.loads(row['extra'])
                    )
                    
                    # Update database
                    cursor.execute('''
                        UPDATE embeddings
                        SET compressed = ?, quantized = ?, reduced = ?, scale = ?, min_val = ?, embedding = ?
                        WHERE id = ?
                    ''', (
                        self.compression_enabled,
                        self.quantization_enabled,
                        self.dimension_reduction_enabled,
                        scale,
                        min_val,
                        processed_data,
                        row['id']
                    ))
                    
                    # Update file cache
                    self._store_in_file(metadata, processed_data, scale, min_val)
                    
                    optimized_count += 1
                    
                except Exception as e:
                    logger.error(f"Error optimizing embedding {row['id']}: {str(e)}")
            
            conn.commit()
            
            # Get total count for reporting
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            total_count = cursor.fetchone()[0]
            
            logger.info(f"Optimized {optimized_count} out of {total_count} embeddings")
            
            return {
                "optimized_count": optimized_count,
                "total_embeddings": total_count
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error optimizing storage: {str(e)}")
            return {"error": str(e)}
        finally:
            conn.close()

# Example usage
def example_usage():
    """Example of using the optimized embedding storage"""
    import random
    
    # Create storage
    storage = OptimizedEmbeddingStorage(
        database_path="embeddings.db",
        compression_enabled=True,
        quantization_enabled=True,
        dimension_reduction_enabled=False
    )
    
    # Create some random embeddings
    dimension = 384
    embeddings = []
    for i in range(10):
        # Create a random unit vector
        vec = [random.uniform(-1, 1) for _ in range(dimension)]
        norm = sum(x**2 for x in vec) ** 0.5
        normalized = [x / norm for x in vec]
        embeddings.append(normalized)
        
        # Store in optimized format
        text = f"This is test text {i} for embedding storage example"
        storage.store(
            text=text,
            embedding=normalized,
            model="test-model",
            tags=["test", f"example-{i}"],
            extra={"test_id": i}
        )
    
    # Get storage stats
    stats = storage.get_stats()
    print(f"Storage stats: {stats}")
    
    # Search for similar embeddings
    query_embedding = embeddings[0]  # Use the first embedding as query
    results = storage.search(query_embedding, top_k=5)
    
    print(f"Search results:")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['text']} (similarity: {result['similarity']:.4f})")
    
    # Optimize storage
    optimization_result = storage.optimize_storage()
    print(f"Optimization result: {optimization_result}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_usage() 