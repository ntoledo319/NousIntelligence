"""
Search functionality routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search', methods=['POST'])
def search_api():
    """Search API endpoint"""
    data = request.get_json() or {}
    query = data.get('query', '')
    
    return jsonify({
        'query': query,
        'results': [
            {'title': 'Demo Result', 'content': f'Search result for: {query}'}
        ]
    })
