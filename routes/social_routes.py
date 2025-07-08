"""
Social Routes

This module defines routes for social and community features including
support groups, peer connections, and anonymous sharing.

@module routes.social_routes
@context_boundary Social Features
"""

import logging
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.social_service import SocialService
from services.gamification_service import GamificationService
from utils.unified_auth import login_required, demo_allowed, get_demo_user

logger = logging.getLogger(__name__)

# Create blueprint
social_bp = Blueprint('social', __name__, url_prefix='/social')

# Initialize services
social_service = SocialService()
gamification_service = GamificationService()

def get_current_user_id():
    """Get current user ID from session"""
    user = session.get('user', {})
    return user.get('id', 'demo_user')

# === Support Group Routes ===

@social_bp.route('/groups')
@demo_allowed
def groups_index():
    """Support groups main page"""
    user_id = get_current_user_id()
    
    # Get user's groups
    my_groups = social_service.get_user_groups(user_id)
    
    # Get available categories
    categories = ['anxiety', 'depression', 'addiction', 'relationships', 'grief', 'general']
    
    return render_template('social/groups.html', 
                         my_groups=my_groups,
                         categories=categories)

@social_bp.route('/groups/search')
@demo_allowed
def search_groups():
    """Search for support groups"""
    category = request.args.get('category')
    query = request.args.get('q')
    
    groups = social_service.search_support_groups(category, query)
    
    return render_template('social/groups_search.html',
                         groups=groups,
                         category=category,
                         query=query)

@social_bp.route('/api/social/groups', methods=['POST'])
@login_required
def api_create_group():
    """API endpoint to create a support group"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name')
    description = data.get('description')
    category = data.get('category')
    privacy_level = data.get('privacy_level', 'private')
    
    if not all([name, description, category]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    group = social_service.create_support_group(
        user_id, name, description, category, privacy_level
    )
    
    if group:
        # Award points for creating a group
        gamification_service.add_points(user_id, 20, 'social', 'Created support group')
        
        return jsonify({
            'success': True,
            'group': group.to_dict()
        })
    else:
        return jsonify({'error': 'Could not create group'}), 500

@social_bp.route('/api/social/groups/<int:group_id>/join', methods=['POST'])
@login_required
def api_join_group(group_id):
    """API endpoint to join a support group"""
    user_id = get_current_user_id()
    
    success = social_service.join_support_group(user_id, group_id)
    
    if success:
        # Award points for joining a group
        gamification_service.add_points(user_id, 10, 'social', 'Joined support group')
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not join group'}), 400

@social_bp.route('/groups/<int:group_id>')
@login_required
def view_group(group_id):
    """View a specific support group"""
    user_id = get_current_user_id()
    
    # Implementation would fetch group details and posts
    return render_template('social/group_detail.html', group_id=group_id)

# === Peer Connection Routes ===

@social_bp.route('/connections')
@demo_allowed
def connections_index():
    """Peer connections page"""
    user_id = get_current_user_id()
    
    connections = social_service.get_user_connections(user_id)
    
    return render_template('social/connections.html',
                         connections=connections)

@social_bp.route('/api/social/connections/request', methods=['POST'])
@login_required
def api_request_connection():
    """API endpoint to request a peer connection"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    peer_id = data.get('peer_id')
    connection_type = data.get('connection_type', 'peer')
    
    if not peer_id:
        return jsonify({'error': 'Peer ID required'}), 400
    
    success = social_service.request_peer_connection(
        user_id, peer_id, connection_type
    )
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not send connection request'}), 400

@social_bp.route('/api/social/connections/<int:connection_id>/accept', methods=['POST'])
@login_required
def api_accept_connection(connection_id):
    """API endpoint to accept a connection request"""
    user_id = get_current_user_id()
    
    success = social_service.accept_peer_connection(user_id, connection_id)
    
    if success:
        # Award points for making connections
        gamification_service.add_points(user_id, 15, 'social', 'Made new connection')
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not accept connection'}), 400

# === Anonymous Sharing Routes ===

@social_bp.route('/share')
@demo_allowed
def share_index():
    """Anonymous sharing main page"""
    category = request.args.get('category')
    
    shares = social_service.get_anonymous_shares(category)
    
    # Get categories
    categories = ['anxiety', 'depression', 'success', 'struggle', 'hope', 'general']
    
    return render_template('social/anonymous_shares.html',
                         shares=shares,
                         categories=categories,
                         selected_category=category)

@social_bp.route('/share/new')
@login_required
def new_share():
    """Create new anonymous share page"""
    return render_template('social/new_share.html')

@social_bp.route('/api/social/shares', methods=['POST'])
@login_required
def api_create_share():
    """API endpoint to create anonymous share"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    category = data.get('category')
    title = data.get('title')
    content = data.get('content')
    mood = data.get('mood')
    
    if not all([category, content]):
        return jsonify({'error': 'Category and content required'}), 400
    
    share = social_service.create_anonymous_share(
        user_id, category, title, content, mood
    )
    
    if share:
        # Award points for sharing
        gamification_service.add_points(user_id, 10, 'social', 'Shared anonymously')
        
        return jsonify({
            'success': True,
            'share_id': share.share_id
        })
    else:
        return jsonify({'error': 'Could not create share'}), 500

@social_bp.route('/api/social/shares/<share_id>/support', methods=['POST'])
@demo_allowed
def api_support_share(share_id):
    """API endpoint to add support to a share"""
    user_id = get_current_user_id()
    
    success = social_service.add_support_to_share(share_id, user_id)
    
    if success:
        # Award points for supporting others
        gamification_service.add_points(user_id, 5, 'social', 'Supported community member')
        
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not add support'}), 400

# === Community Stats Route ===

@social_bp.route('/api/social/stats')
@demo_allowed
def api_community_stats():
    """Get user's community engagement statistics"""
    user_id = get_current_user_id()
    
    stats = social_service.get_community_stats(user_id)
    
    return jsonify(stats)


# AI-GENERATED [2024-12-01]
# @see services.social_service for business logic
# NON-NEGOTIABLES: Maintain anonymity in anonymous sharing features 