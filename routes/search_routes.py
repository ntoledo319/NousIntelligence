"""
Search Routes

This module provides API endpoints for global search functionality.
"""

from flask import Blueprint, request, jsonify, session
import logging

# Create blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api/v1/search')

logger = logging.getLogger(__name__)

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in session

@search_bp.route('/', methods=['GET'])
def search_all():
    """Search across all user content"""
    # Allow public search with limited results for guests
    if not is_authenticated():
        query = request.args.get('q', '').strip()
        return jsonify({
            'success': True,
            'data': {
                'results': [{'title': f'Demo search result for: {query}', 'content': 'Sign up for full search capabilities', 'type': 'demo'}],
                'total': 1,
                'demo_mode': True
            }
        })
    
    try:
        from app import db
        from utils.search_service import SearchService
        
        user_id = session['user']['id']
        query = request.args.get('q', '').strip()
        content_types = request.args.getlist('types')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        search_service = SearchService(db)
        results = search_service.search_all_content(
            user_id, query, content_types, limit, offset
        )
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@search_bp.route('/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.search_service import SearchService
        
        user_id = session['user']['id']
        partial_query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        search_service = SearchService(db)
        suggestions = search_service.get_search_suggestions(user_id, partial_query, limit)
        
        return jsonify({
            'success': True,
            'data': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {str(e)}")
        return jsonify({'error': 'Failed to get suggestions'}), 500

@search_bp.route('/index', methods=['POST'])
def index_content():
    """Index content for search"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.search_service import SearchService
        
        user_id = session['user']['id']
        data = request.get_json()
        
        required_fields = ['content_type', 'content_id', 'title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        search_service = SearchService(db)
        success = search_service.index_content(
            user_id=user_id,
            content_type=data['content_type'],
            content_id=data['content_id'],
            title=data['title'],
            content=data['content'],
            tags=data.get('tags', [])
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Content indexed successfully'
            })
        else:
            return jsonify({'error': 'Failed to index content'}), 500
            
    except Exception as e:
        logger.error(f"Error indexing content: {str(e)}")
        return jsonify({'error': 'Failed to index content'}), 500

@search_bp.route('/by-type/<content_type>', methods=['GET'])
def search_by_type(content_type):
    """Search within a specific content type"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.search_service import SearchService
        
        user_id = session['user']['id']
        query = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        search_service = SearchService(db)
        results = search_service.search_by_type(user_id, content_type, query, limit)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Error searching by type: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@search_bp.route('/tags', methods=['GET'])
def get_popular_tags():
    """Get popular tags for the user"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.search_service import SearchService
        
        user_id = session['user']['id']
        limit = request.args.get('limit', 20, type=int)
        
        search_service = SearchService(db)
        tags = search_service.get_popular_tags(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': tags
        })
        
    except Exception as e:
        logger.error(f"Error getting popular tags: {str(e)}")
        return jsonify({'error': 'Failed to get tags'}), 500

@search_bp.route('/summary', methods=['GET'])
def get_content_summary():
    """Get summary of searchable content"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.search_service import SearchService
        
        user_id = session['user']['id']
        
        search_service = SearchService(db)
        summary = search_service.get_content_type_summary(user_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting content summary: {str(e)}")
        return jsonify({'error': 'Failed to get summary'}), 500

@search_bp.route('/index/<content_type>/<content_id>', methods=['DELETE'])
def remove_from_index(content_type, content_id):
    """Remove content from search index"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.search_service import SearchService
        
        user_id = session['user']['id']
        
        search_service = SearchService(db)
        success = search_service.remove_from_index(user_id, content_type, content_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Content removed from index'
            })
        else:
            return jsonify({'error': 'Content not found in index'}), 404
            
    except Exception as e:
        logger.error(f"Error removing from index: {str(e)}")
        return jsonify({'error': 'Failed to remove from index'}), 500
