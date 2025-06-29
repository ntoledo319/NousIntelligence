"""
Enhanced Caching System - Maximum Cost Reduction Through Intelligent Caching
Implements multi-layer caching with semantic similarity and smart invalidation
"""

import os
import json
import time
import hashlib
import logging
import sqlite3
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import pickle
import gzip

logger = logging.getLogger(__name__)

class EnhancedCachingSystem:
    """Multi-layer caching system for maximum cost optimization"""
    
    def __init__(self):
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "enhanced_cache.db"
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'invalidations': 0
        }
        self.init_database()
        self._lock = threading.Lock()
    
    def init_database(self):
        """Initialize enhanced cache database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            
            # AI Response Cache
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ai_response_cache (
                    id INTEGER PRIMARY KEY,
                    prompt_hash TEXT,
                    prompt_text TEXT,
                    response_text TEXT,
                    provider TEXT,
                    model TEXT,
                    tokens_used INTEGER,
                    quality_score REAL,
                    semantic_tags TEXT,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    user_rating REAL,
                    expires_at TIMESTAMP
                )
            ''')
            
            # Database Query Cache
            conn.execute('''
                CREATE TABLE IF NOT EXISTS query_cache (
                    id INTEGER PRIMARY KEY,
                    query_hash TEXT UNIQUE,
                    query_text TEXT,
                    result_data BLOB,
                    table_names TEXT,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    expires_at TIMESTAMP
                )
            ''')
            
            # Voice Processing Cache
            conn.execute('''
                CREATE TABLE IF NOT EXISTS voice_cache (
                    id INTEGER PRIMARY KEY,
                    audio_hash TEXT UNIQUE,
                    transcription TEXT,
                    voice_synthesis BLOB,
                    language TEXT,
                    quality_score REAL,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 1
                )
            ''')
            
            # API Response Cache
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_cache (
                    id INTEGER PRIMARY KEY,
                    endpoint_hash TEXT,
                    endpoint_url TEXT,
                    request_params TEXT,
                    response_data BLOB,
                    status_code INTEGER,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP,
                    expires_at TIMESTAMP,
                    cache_strategy TEXT
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_ai_prompt_hash ON ai_response_cache(prompt_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_query_hash ON query_cache(query_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_voice_hash ON voice_cache(audio_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_api_hash ON api_cache(endpoint_hash)')
            
            conn.commit()
            conn.close()
            logger.info("Enhanced caching database initialized")
            
        except Exception as e:
            logger.error(f"Cache database initialization failed: {e}")
    
    def get_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        # Simple word overlap similarity (can be enhanced with embeddings)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def cache_ai_response(self, prompt: str, response: str, provider: str, 
                         model: str = "", tokens_used: int = 0, quality_score: float = 0.8,
                         user_rating: float = None, ttl_hours: int = 168) -> bool:
        """Cache AI response with enhanced metadata"""
        try:
            with self._lock:
                prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
                
                # Extract semantic tags
                semantic_tags = self._extract_semantic_tags(prompt)
                
                # Calculate expiration
                expires_at = datetime.now() + timedelta(hours=ttl_hours)
                
                conn = sqlite3.connect(str(self.db_path))
                conn.execute('''
                    INSERT OR REPLACE INTO ai_response_cache 
                    (prompt_hash, prompt_text, response_text, provider, model, tokens_used,
                     quality_score, semantic_tags, created_at, last_accessed, user_rating, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?, ?)
                ''', (prompt_hash, prompt, response, provider, model, tokens_used,
                      quality_score, json.dumps(semantic_tags), user_rating, expires_at))
                
                conn.commit()
                conn.close()
                
                # Also cache in memory for fastest access
                self.memory_cache[prompt_hash] = {
                    'response': response,
                    'provider': provider,
                    'quality_score': quality_score,
                    'cached_at': time.time()
                }
                
                self.cache_stats['saves'] += 1
                return True
                
        except Exception as e:
            logger.error(f"AI response caching error: {e}")
            return False
    
    def get_cached_ai_response(self, prompt: str, similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """Get cached AI response with semantic similarity matching"""
        try:
            with self._lock:
                prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
                
                # Check memory cache first
                if prompt_hash in self.memory_cache:
                    cached = self.memory_cache[prompt_hash]
                    # Check if still fresh (1 hour in memory)
                    if time.time() - cached['cached_at'] < 3600:
                        self.cache_stats['hits'] += 1
                        return cached
                    else:
                        del self.memory_cache[prompt_hash]
                
                conn = sqlite3.connect(str(self.db_path))
                
                # First try exact match
                cursor = conn.execute('''
                    SELECT response_text, provider, model, quality_score, access_count
                    FROM ai_response_cache 
                    WHERE prompt_hash = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
                    ORDER BY quality_score DESC, access_count DESC
                    LIMIT 1
                ''', (prompt_hash,))
                
                result = cursor.fetchone()
                if result:
                    # Update access statistics
                    conn.execute('''
                        UPDATE ai_response_cache 
                        SET last_accessed = datetime('now'), access_count = access_count + 1
                        WHERE prompt_hash = ?
                    ''', (prompt_hash,))
                    conn.commit()
                    conn.close()
                    
                    self.cache_stats['hits'] += 1
                    return {
                        'response': result[0],
                        'provider': result[1],
                        'model': result[2],
                        'quality_score': result[3],
                        'cached': True,
                        'match_type': 'exact'
                    }
                
                # If no exact match, try semantic similarity
                cursor = conn.execute('''
                    SELECT prompt_text, response_text, provider, model, quality_score
                    FROM ai_response_cache 
                    WHERE (expires_at IS NULL OR expires_at > datetime('now'))
                    AND quality_score > 0.7
                    ORDER BY quality_score DESC
                    LIMIT 20
                ''')
                
                candidates = cursor.fetchall()
                best_match = None
                best_similarity = 0
                
                for candidate in candidates:
                    similarity = self.get_semantic_similarity(prompt, candidate[0])
                    if similarity > similarity_threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = candidate
                
                conn.close()
                
                if best_match:
                    self.cache_stats['hits'] += 1
                    return {
                        'response': best_match[1],
                        'provider': best_match[2],
                        'model': best_match[3],
                        'quality_score': best_match[4],
                        'cached': True,
                        'match_type': 'semantic',
                        'similarity_score': best_similarity
                    }
                
                self.cache_stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"AI response cache retrieval error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def cache_database_query(self, query: str, result: Any, table_names: List[str] = None, 
                           ttl_hours: int = 24) -> bool:
        """Cache database query result"""
        try:
            with self._lock:
                query_hash = hashlib.sha256(query.encode()).hexdigest()
                
                # Serialize result
                result_data = pickle.dumps(result)
                compressed_data = gzip.compress(result_data)
                
                expires_at = datetime.now() + timedelta(hours=ttl_hours)
                
                conn = sqlite3.connect(str(self.db_path))
                conn.execute('''
                    INSERT OR REPLACE INTO query_cache 
                    (query_hash, query_text, result_data, table_names, created_at, last_accessed, expires_at)
                    VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), ?)
                ''', (query_hash, query, compressed_data, json.dumps(table_names or []), expires_at))
                
                conn.commit()
                conn.close()
                
                self.cache_stats['saves'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Database query caching error: {e}")
            return False
    
    def get_cached_database_query(self, query: str) -> Optional[Any]:
        """Get cached database query result"""
        try:
            with self._lock:
                query_hash = hashlib.sha256(query.encode()).hexdigest()
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute('''
                    SELECT result_data FROM query_cache 
                    WHERE query_hash = ? AND (expires_at IS NULL OR expires_at > datetime('now'))
                    LIMIT 1
                ''', (query_hash,))
                
                result = cursor.fetchone()
                if result:
                    # Update access statistics
                    conn.execute('''
                        UPDATE query_cache 
                        SET last_accessed = datetime('now'), access_count = access_count + 1
                        WHERE query_hash = ?
                    ''', (query_hash,))
                    conn.commit()
                    
                    # Deserialize result
                    compressed_data = result[0]
                    result_data = gzip.decompress(compressed_data)
                    cached_result = pickle.loads(result_data)
                    
                    conn.close()
                    self.cache_stats['hits'] += 1
                    return cached_result
                
                conn.close()
                self.cache_stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Database query cache retrieval error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def invalidate_cache_by_tables(self, table_names: List[str]):
        """Invalidate cached queries that depend on specific tables"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                
                for table_name in table_names:
                    conn.execute('''
                        DELETE FROM query_cache 
                        WHERE table_names LIKE ? OR table_names LIKE ? OR table_names LIKE ?
                    ''', (f'%"{table_name}"%', f'%{table_name}%', f'%{table_name.lower()}%'))
                
                conn.commit()
                conn.close()
                
                self.cache_stats['invalidations'] += len(table_names)
                logger.info(f"Invalidated cache for tables: {table_names}")
                
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def cache_voice_processing(self, audio_data: bytes, transcription: str = "", 
                             synthesis_data: bytes = b"", language: str = "en",
                             quality_score: float = 0.8) -> bool:
        """Cache voice processing results"""
        try:
            with self._lock:
                audio_hash = hashlib.sha256(audio_data).hexdigest()
                
                conn = sqlite3.connect(str(self.db_path))
                conn.execute('''
                    INSERT OR REPLACE INTO voice_cache 
                    (audio_hash, transcription, voice_synthesis, language, quality_score,
                     created_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                ''', (audio_hash, transcription, synthesis_data, language, quality_score))
                
                conn.commit()
                conn.close()
                
                self.cache_stats['saves'] += 1
                return True
                
        except Exception as e:
            logger.error(f"Voice processing caching error: {e}")
            return False
    
    def get_cached_voice_processing(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """Get cached voice processing result"""
        try:
            with self._lock:
                audio_hash = hashlib.sha256(audio_data).hexdigest()
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute('''
                    SELECT transcription, voice_synthesis, language, quality_score
                    FROM voice_cache 
                    WHERE audio_hash = ?
                    LIMIT 1
                ''', (audio_hash,))
                
                result = cursor.fetchone()
                if result:
                    # Update access statistics
                    conn.execute('''
                        UPDATE voice_cache 
                        SET last_accessed = datetime('now'), access_count = access_count + 1
                        WHERE audio_hash = ?
                    ''', (audio_hash,))
                    conn.commit()
                    conn.close()
                    
                    self.cache_stats['hits'] += 1
                    return {
                        'transcription': result[0],
                        'synthesis_data': result[1],
                        'language': result[2],
                        'quality_score': result[3],
                        'cached': True
                    }
                
                conn.close()
                self.cache_stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Voice cache retrieval error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def _extract_semantic_tags(self, text: str) -> List[str]:
        """Extract semantic tags from text for better caching"""
        tags = []
        text_lower = text.lower()
        
        # Task-related tags
        if any(word in text_lower for word in ['task', 'todo', 'remind', 'schedule']):
            tags.append('task_management')
        
        # Health-related tags
        if any(word in text_lower for word in ['health', 'wellness', 'exercise', 'mood']):
            tags.append('health_tracking')
        
        # Analysis tags
        if any(word in text_lower for word in ['analyze', 'analysis', 'pattern', 'trend']):
            tags.append('analysis')
        
        # Financial tags
        if any(word in text_lower for word in ['money', 'budget', 'expense', 'financial']):
            tags.append('financial')
        
        # Communication tags
        if any(word in text_lower for word in ['hello', 'hi', 'thank', 'please']):
            tags.append('communication')
        
        return tags
    
    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                
                # Clean expired AI responses
                cursor = conn.execute('DELETE FROM ai_response_cache WHERE expires_at < datetime("now")')
                ai_deleted = cursor.rowcount
                
                # Clean expired queries
                cursor = conn.execute('DELETE FROM query_cache WHERE expires_at < datetime("now")')
                query_deleted = cursor.rowcount
                
                # Clean expired API responses
                cursor = conn.execute('DELETE FROM api_cache WHERE expires_at < datetime("now")')
                api_deleted = cursor.rowcount
                
                # Clean old voice cache (keep for 7 days)
                cursor = conn.execute('''
                    DELETE FROM voice_cache 
                    WHERE created_at < datetime('now', '-7 days')
                ''')
                voice_deleted = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                # Clean memory cache
                current_time = time.time()
                expired_keys = [
                    key for key, value in self.memory_cache.items()
                    if current_time - value['cached_at'] > 3600  # 1 hour
                ]
                for key in expired_keys:
                    del self.memory_cache[key]
                
                logger.info(f"Cache cleanup: AI:{ai_deleted}, Query:{query_deleted}, API:{api_deleted}, Voice:{voice_deleted}, Memory:{len(expired_keys)}")
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                
                # Count cache entries
                ai_count = conn.execute('SELECT COUNT(*) FROM ai_response_cache').fetchone()[0]
                query_count = conn.execute('SELECT COUNT(*) FROM query_cache').fetchone()[0]
                voice_count = conn.execute('SELECT COUNT(*) FROM voice_cache').fetchone()[0]
                api_count = conn.execute('SELECT COUNT(*) FROM api_cache').fetchone()[0]
                
                # Calculate hit rates
                total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
                hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
                
                # Database size
                db_size = os.path.getsize(str(self.db_path)) if os.path.exists(str(self.db_path)) else 0
                
                conn.close()
                
                return {
                    'cache_entries': {
                        'ai_responses': ai_count,
                        'database_queries': query_count,
                        'voice_processing': voice_count,
                        'api_responses': api_count,
                        'memory_cache': len(self.memory_cache)
                    },
                    'performance': {
                        'hit_rate_percentage': hit_rate,
                        'total_hits': self.cache_stats['hits'],
                        'total_misses': self.cache_stats['misses'],
                        'total_saves': self.cache_stats['saves'],
                        'total_invalidations': self.cache_stats['invalidations']
                    },
                    'storage': {
                        'database_size_bytes': db_size,
                        'database_size_mb': db_size / (1024 * 1024)
                    }
                }
                
        except Exception as e:
            logger.error(f"Cache statistics error: {e}")
            return {'error': str(e)}

# Global instance
_caching_system = None

def get_caching_system() -> EnhancedCachingSystem:
    """Get or create global caching system instance"""
    global _caching_system
    if _caching_system is None:
        _caching_system = EnhancedCachingSystem()
    return _caching_system

# Convenience functions
def cache_ai_response(prompt: str, response: str, provider: str, **kwargs) -> bool:
    """Cache AI response"""
    return get_caching_system().cache_ai_response(prompt, response, provider, **kwargs)

def get_cached_ai_response(prompt: str, similarity_threshold: float = 0.8) -> Optional[Dict[str, Any]]:
    """Get cached AI response"""
    return get_caching_system().get_cached_ai_response(prompt, similarity_threshold)

def cache_database_query(query: str, result: Any, table_names: List[str] = None) -> bool:
    """Cache database query result"""
    return get_caching_system().cache_database_query(query, result, table_names)

def get_cached_database_query(query: str) -> Optional[Any]:
    """Get cached database query result"""
    return get_caching_system().get_cached_database_query(query)

logger.info("Enhanced Caching System initialized - maximum cost reduction through intelligent multi-layer caching")