"""
Search Service

This module provides global search functionality across all user content in the NOUS application.
Supports semantic search, filtering, and indexing of user data.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import and_, or_, func, text

logger = logging.getLogger(__name__)

class SearchService:
    """Service for global search functionality"""
    
    def __init__(self, db):
        self.db = db
    
    def search_all_content(self, user_id: str, query: str, content_types: List[str] = None, 
                          limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Search across all user content"""
        try:
            from models.analytics_models import SearchIndex
            
            # Build base query
            search_query = self.db.session.query(SearchIndex).filter(
                SearchIndex.user_id == user_id
            )
            
            # Filter by content types if specified
            if content_types:
                search_query = search_query.filter(
                    SearchIndex.content_type.in_(content_types)
                )
            
            # Apply text search
            if query.strip():
                search_terms = self._prepare_search_terms(query)
                
                # Search in title and content
                title_filter = or_(*[
                    SearchIndex.title.ilike(f'%{term}%') for term in search_terms
                ])
                content_filter = or_(*[
                    SearchIndex.content.ilike(f'%{term}%') for term in search_terms
                ])
                
                search_query = search_query.filter(
                    or_(title_filter, content_filter)
                )
            
            # Get total count
            total_count = search_query.count()
            
            # Apply pagination and ordering
            results = search_query.order_by(
                SearchIndex.updated_at.desc()
            ).offset(offset).limit(limit).all()
            
            # Group results by content type
            grouped_results = self._group_results_by_type(results)
            
            # Get content type counts
            type_counts = self._get_content_type_counts(user_id, query)
            
            return {
                'query': query,
                'total_count': total_count,
                'results': [result.to_dict() for result in results],
                'grouped_results': grouped_results,
                'type_counts': type_counts,
                'has_more': total_count > (offset + limit),
                'next_offset': offset + limit if total_count > (offset + limit) else None
            }
            
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return {
                'query': query,
                'total_count': 0,
                'results': [],
                'grouped_results': {},
                'type_counts': {},
                'has_more': False,
                'next_offset': None
            }
    
    def search_by_type(self, user_id: str, content_type: str, query: str = '', 
                      limit: int = 20) -> List[Dict]:
        """Search within a specific content type"""
        try:
            from models.analytics_models import SearchIndex
            
            search_query = self.db.session.query(SearchIndex).filter(
                and_(
                    SearchIndex.user_id == user_id,
                    SearchIndex.content_type == content_type
                )
            )
            
            if query.strip():
                search_terms = self._prepare_search_terms(query)
                filters = []
                
                for term in search_terms:
                    filters.append(SearchIndex.title.ilike(f'%{term}%'))
                    filters.append(SearchIndex.content.ilike(f'%{term}%'))
                
                search_query = search_query.filter(or_(*filters))
            
            results = search_query.order_by(
                SearchIndex.updated_at.desc()
            ).limit(limit).all()
            
            return [result.to_dict() for result in results]
            
        except Exception as e:
            logger.error(f"Error searching by type: {str(e)}")
            return []
    
    def get_search_suggestions(self, user_id: str, partial_query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            from models.analytics_models import SearchIndex
            
            if len(partial_query.strip()) < 2:
                return []
            
            # Get unique titles and content snippets that match
            results = self.db.session.query(SearchIndex.title).filter(
                and_(
                    SearchIndex.user_id == user_id,
                    SearchIndex.title.ilike(f'%{partial_query}%')
                )
            ).distinct().limit(limit).all()
            
            suggestions = []
            for result in results:
                if result.title and result.title not in suggestions:
                    suggestions.append(result.title)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []
    
    def index_content(self, user_id: str, content_type: str, content_id: str, 
                     title: str, content: str, tags: List[str] = None) -> bool:
        """Index content for search"""
        try:
            from models.analytics_models import SearchIndex
            
            # Check if item already exists
            existing = self.db.session.query(SearchIndex).filter(
                and_(
                    SearchIndex.user_id == user_id,
                    SearchIndex.content_type == content_type,
                    SearchIndex.content_id == content_id
                )
            ).first()
            
            if existing:
                # Update existing
                existing.title = title
                existing.content = content
                existing.tags = tags or []
                existing.search_vector = self._create_search_vector(title, content, tags)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                search_item = SearchIndex(
                    user_id=user_id,
                    content_type=content_type,
                    content_id=content_id,
                    title=title,
                    content=content,
                    tags=tags or [],
                    search_vector=self._create_search_vector(title, content, tags)
                )
                self.db.session.add(search_item)
            
            self.db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error indexing content: {str(e)}")
            self.db.session.rollback()
            return False
    
    def remove_from_index(self, user_id: str, content_type: str, content_id: str) -> bool:
        """Remove content from search index"""
        try:
            from models.analytics_models import SearchIndex
            
            item = self.db.session.query(SearchIndex).filter(
                and_(
                    SearchIndex.user_id == user_id,
                    SearchIndex.content_type == content_type,
                    SearchIndex.content_id == content_id
                )
            ).first()
            
            if item:
                self.db.session.delete(item)
                self.db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing from index: {str(e)}")
            self.db.session.rollback()
            return False
    
    def get_popular_tags(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular tags for the user"""
        try:
            from models.analytics_models import SearchIndex
            
            # Get all tags
            results = self.db.session.query(SearchIndex.tags).filter(
                SearchIndex.user_id == user_id
            ).all()
            
            tag_counts = {}
            for result in results:
                if result.tags:
                    for tag in result.tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Sort by count and return top tags
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            return [{'tag': tag, 'count': count} for tag, count in sorted_tags]
            
        except Exception as e:
            logger.error(f"Error getting popular tags: {str(e)}")
            return []
    
    def get_content_type_summary(self, user_id: str) -> Dict[str, int]:
        """Get summary of content types for user"""
        try:
            from models.analytics_models import SearchIndex
            
            results = self.db.session.query(
                SearchIndex.content_type,
                func.count(SearchIndex.id)
            ).filter(
                SearchIndex.user_id == user_id
            ).group_by(SearchIndex.content_type).all()
            
            return {content_type: count for content_type, count in results}
            
        except Exception as e:
            logger.error(f"Error getting content type summary: {str(e)}")
            return {}
    
    def _prepare_search_terms(self, query: str) -> List[str]:
        """Prepare search terms from query"""
        # Remove special characters and split into terms
        clean_query = re.sub(r'[^\w\s]', ' ', query.lower())
        terms = [term.strip() for term in clean_query.split() if len(term.strip()) > 2]
        return terms
    
    def _group_results_by_type(self, results) -> Dict[str, List[Dict]]:
        """Group search results by content type"""
        grouped = {}
        for result in results:
            content_type = result.content_type
            if content_type not in grouped:
                grouped[content_type] = []
            grouped[content_type].append(result.to_dict())
        
        return grouped
    
    def _get_content_type_counts(self, user_id: str, query: str) -> Dict[str, int]:
        """Get counts by content type for current search"""
        try:
            from models.analytics_models import SearchIndex
            
            base_query = self.db.session.query(SearchIndex).filter(
                SearchIndex.user_id == user_id
            )
            
            if query.strip():
                search_terms = self._prepare_search_terms(query)
                filters = []
                
                for term in search_terms:
                    filters.append(SearchIndex.title.ilike(f'%{term}%'))
                    filters.append(SearchIndex.content.ilike(f'%{term}%'))
                
                base_query = base_query.filter(or_(*filters))
            
            results = base_query.with_entities(
                SearchIndex.content_type,
                func.count(SearchIndex.id)
            ).group_by(SearchIndex.content_type).all()
            
            return {content_type: count for content_type, count in results}
            
        except Exception as e:
            logger.error(f"Error getting content type counts: {str(e)}")
            return {}
    
    def _create_search_vector(self, title: str, content: str, tags: List[str] = None) -> str:
        """Create search vector for full-text search"""
        # Combine title, content, and tags for search
        search_text = []
        
        if title:
            search_text.append(title)
        
        if content:
            # Limit content length for search vector
            search_text.append(content[:1000])
        
        if tags:
            search_text.extend(tags)
        
        return ' '.join(search_text).lower()
