"""
from utils.auth_compat import get_demo_user
Search functionality routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user()

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
