"""
Content Service

Manages therapeutic content loading, retrieval, and semantic search.
Uses nous_core.semantic for intelligent retrieval of psychoeducation.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from flask import current_app

# Try to import nous_core semantic, fallback to simple keyword search
try:
    from nous_core.semantic.semantic_index import SemanticIndex
    _HAS_SEMANTIC = True
except ImportError:
    _HAS_SEMANTIC = False

logger = logging.getLogger(__name__)

class ContentService:
    _instance = None

    def __init__(self, content_path: str = 'content/therapy_content.json'):
        self.content_path = content_path
        self.content: Dict[str, Any] = {}
        self.semantic_index = None
        self._load_content()
        self._init_semantic_index()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_content(self):
        """Loads structured content from JSON file"""
        if not os.path.exists(self.content_path):
            logger.error(f"Content file not found at {self.content_path}")
            return

        try:
            with open(self.content_path, 'r') as f:
                self.content = json.load(f)
            logger.info("Therapeutic content loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load therapeutic content: {e}")

    def _init_semantic_index(self):
        """Initializes semantic index for psychoeducation articles"""
        if not _HAS_SEMANTIC:
            logger.warning("nous_core.semantic not available, using keyword fallback")
            return

        try:
            # Create/Get index
            db_path = os.path.join(os.getcwd(), 'instance', 'semantic_index.db')
            self.semantic_index = SemanticIndex(db_path)

            # Index psychoeducation articles
            articles = self.content.get('psychoeducation', [])
            items = []
            for art in articles:
                doc_id = f"psycho_{art['id']}"
                text = f"{art['title']}\n{art['content']}"
                meta = {'type': 'psychoeducation', 'title': art['title']}
                items.append((doc_id, text, meta))

            if items:
                self.semantic_index.bulk_upsert(items)
                logger.info(f"Indexed {len(items)} psychoeducation articles")

        except Exception as e:
            logger.error(f"Failed to initialize semantic index: {e}")
            self.semantic_index = None

    def get_intervention(self, type_id: str, name_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific intervention script (e.g. cbt/thought_record)"""
        return self.content.get(type_id, {}).get(name_id)

    def search_psychoeducation(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Searches psychoeducation content using semantic search or keyword fallback"""
        if self.semantic_index:
            try:
                results = self.semantic_index.search(query, top_k=top_k)
                # Format for usage
                return [
                    {
                        'id': r['doc_id'].replace('psycho_', ''),
                        'title': r['meta'].get('title'),
                        'content': r['text'],
                        'score': r['score']
                    }
                    for r in results
                ]
            except Exception as e:
                logger.error(f"Semantic search error: {e}")

        # Fallback: Simple keyword matching
        query = query.lower()
        results = []
        for art in self.content.get('psychoeducation', []):
            if query in art['title'].lower() or query in art['content'].lower():
                results.append(art)
        return results[:top_k]

# Singleton accessor
def get_content_service():
    return ContentService.get_instance()
