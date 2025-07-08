"""
Mental Health Resources Routes

This module provides routes for accessing crisis support, therapy providers,
and psychiatry options with location-based search.

@module routes.mental_health_resources_routes
@context_boundary Crisis Support & Mental Health Resources
"""

import logging
from flask import Blueprint, render_template, request, jsonify, session, abort
from services.mental_health_resources_service import MentalHealthResourcesService
from utils.unified_auth import login_required, demo_allowed

logger = logging.getLogger(__name__)

# Create blueprint - shorter URL for crisis accessibility
resources_bp = Blueprint('resources', __name__, url_prefix='/resources')

# Initialize service
resources_service = MentalHealthResourcesService()

def get_current_user_id():
    """Get current user ID from session"""
    user = session.get('user', {})
    return user.get('id', 'demo_user')

# === CRITICAL: Crisis Routes (No Authentication Required) ===

@resources_bp.route('/crisis')
def crisis_resources():
    """
    Crisis resources page - ALWAYS ACCESSIBLE
    
    NON-NEGOTIABLES: This route must never require authentication
    """
    # Get user's location if available
    country = request.args.get('country', 'US')
    state = request.args.get('state')
    
    # Get crisis resources
    resources = resources_service.get_crisis_resources(country, state)
    
    # Always show this page, even if template is missing
    try:
        return render_template('resources/crisis.html',
                             resources=resources,
                             country=country,
                             state=state)
    except:
        # Fallback HTML if template doesn't exist
        html = """
        <html>
        <head>
            <title>Crisis Support - Immediate Help Available</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                .crisis-box { background: #ff4444; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                .resource { background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .phone { font-size: 24px; font-weight: bold; }
                a { color: #0066cc; }
            </style>
        </head>
        <body>
            <div class="crisis-box">
                <h1>🆘 Crisis Support - You're Not Alone</h1>
                <p>If you're in immediate danger, call 911 or your local emergency number.</p>
            </div>
            
            <h2>24/7 Crisis Support (US):</h2>
        """
        
        for resource in resources[:5]:  # Show top 5 resources
            if isinstance(resource, dict):
                html += f"""
                <div class="resource">
                    <h3>{resource.get('name', 'Crisis Support')}</h3>
                    <p>{resource.get('description', '')}</p>
                    {f'<p class="phone">📞 Call: {resource["phone_number"]}</p>' if resource.get('phone_number') else ''}
                    {f'<p>💬 Text: {resource["text_number"]}</p>' if resource.get('text_number') else ''}
                </div>
                """
            else:
                html += f"""
                <div class="resource">
                    <h3>{resource.name}</h3>
                    <p>{resource.description}</p>
                    {f'<p class="phone">📞 Call: {resource.phone_number}</p>' if resource.phone_number else ''}
                    {f'<p>💬 Text: {resource.text_number}</p>' if resource.text_number else ''}
                </div>
                """
        
        html += """
            <p><a href="/">← Return to NOUS</a></p>
        </body>
        </html>
        """
        
        return html

@resources_bp.route('/api/crisis', methods=['GET'])
def api_crisis_resources():
    """
    API endpoint for crisis resources - ALWAYS ACCESSIBLE
    
    Used by chat and other features to quickly get crisis info
    """
    country = request.args.get('country', 'US')
    state = request.args.get('state')
    specialization = request.args.get('specialization')
    
    resources = resources_service.get_crisis_resources(country, state, specialization)
    
    return jsonify({
        'resources': [r.to_dict() if hasattr(r, 'to_dict') else r for r in resources],
        'disclaimer': 'If you are in immediate danger, please call 911 or your local emergency services.'
    })

# === Therapy Provider Routes ===

@resources_bp.route('/therapy')
@demo_allowed
def therapy_search():
    """Therapy provider search page"""
    return render_template('resources/therapy_search.html')

@resources_bp.route('/api/therapy/search', methods=['POST'])
@demo_allowed
def api_search_therapy():
    """Search for therapy providers near a location"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No search parameters provided'}), 400
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        # Try city/state search
        city = data.get('city')
        state = data.get('state')
        
        if city and state:
            providers = resources_service.get_affordable_therapy_options(city, state)
        else:
            return jsonify({'error': 'Location required (latitude/longitude or city/state)'}), 400
    else:
        # Location-based search
        radius = data.get('radius_miles', 25)
        filters = {
            'has_sliding_scale': data.get('affordable_only', False),
            'accepts_insurance': data.get('accepts_insurance'),
            'is_online': data.get('online_only', False),
            'specialization': data.get('specialization'),
            'modality': data.get('modality'),
            'max_fee': data.get('max_session_fee')
        }
        
        providers = resources_service.search_therapy_providers(
            latitude, longitude, radius, filters
        )
    
    return jsonify({
        'providers': [p.to_dict() for p in providers],
        'count': len(providers)
    })

# === Psychiatry Provider Routes ===

@resources_bp.route('/psychiatry')
@demo_allowed
def psychiatry_search():
    """Psychiatry provider search page"""
    return render_template('resources/psychiatry_search.html')

@resources_bp.route('/api/psychiatry/search', methods=['POST'])
@demo_allowed
def api_search_psychiatry():
    """Search for psychiatry providers"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No search parameters provided'}), 400
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'error': 'Location required (latitude/longitude)'}), 400
    
    radius = data.get('radius_miles', 50)
    filters = {
        'accepts_medicare': data.get('accepts_medicare', False),
        'accepts_medicaid': data.get('accepts_medicaid', False),
        'is_telehealth': data.get('telehealth_available', False),
        'specialization': data.get('specialization')
    }
    
    providers = resources_service.search_psychiatry_providers(
        latitude, longitude, radius, filters
    )
    
    return jsonify({
        'providers': [p.to_dict() for p in providers],
        'count': len(providers)
    })

# === Community Resources Routes ===

@resources_bp.route('/community')
@demo_allowed
def community_resources():
    """Community mental health resources page"""
    city = request.args.get('city')
    state = request.args.get('state')
    
    if not city or not state:
        return render_template('resources/community_search.html')
    
    resources = resources_service.get_community_resources(city, state)
    
    return render_template('resources/community_resources.html',
                         resources=resources,
                         city=city,
                         state=state)

@resources_bp.route('/api/community/<city>/<state>')
@demo_allowed
def api_community_resources(city, state):
    """Get community resources for a location"""
    resource_type = request.args.get('type')
    
    resources = resources_service.get_community_resources(city, state, resource_type)
    
    return jsonify({
        'resources': [r.to_dict() for r in resources],
        'location': {'city': city, 'state': state}
    })

# === Saved Resources Routes (Requires Authentication) ===

@resources_bp.route('/api/save', methods=['POST'])
@login_required
def api_save_resource():
    """Save a resource to user's list"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    resource_type = data.get('resource_type')
    resource_id = data.get('resource_id')
    notes = data.get('notes')
    is_primary = data.get('is_primary', False)
    
    if not resource_type or not resource_id:
        return jsonify({'error': 'Resource type and ID required'}), 400
    
    success = resources_service.save_user_resource(
        user_id, resource_type, resource_id, notes, is_primary
    )
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not save resource'}), 500

@resources_bp.route('/saved')
@login_required
def saved_resources():
    """View user's saved resources"""
    user_id = get_current_user_id()
    
    resources = resources_service.get_user_saved_resources(user_id)
    
    return render_template('resources/saved.html', resources=resources)

@resources_bp.route('/api/saved')
@login_required
def api_saved_resources():
    """Get user's saved resources"""
    user_id = get_current_user_id()
    
    resources = resources_service.get_user_saved_resources(user_id)
    
    return jsonify(resources)

# === Quick Access Route ===

@resources_bp.route('/quick-help')
def quick_help():
    """Quick access page with all resource types"""
    # This page should load even without location
    return render_template('resources/quick_help.html')

# === Location Helper Route ===

@resources_bp.route('/api/geocode', methods=['POST'])
@demo_allowed
def api_geocode():
    """Convert address to coordinates (would integrate with geocoding service)"""
    data = request.get_json()
    
    # This is a placeholder - would integrate with Google Maps or similar
    # For now, return common US city coordinates
    city_coords = {
        'new york': {'lat': 40.7128, 'lng': -74.0060},
        'los angeles': {'lat': 34.0522, 'lng': -118.2437},
        'chicago': {'lat': 41.8781, 'lng': -87.6298},
        'houston': {'lat': 29.7604, 'lng': -95.3698},
        'phoenix': {'lat': 33.4484, 'lng': -112.0740},
    }
    
    city = data.get('city', '').lower()
    if city in city_coords:
        return jsonify({
            'success': True,
            'coordinates': city_coords[city]
        })
    
    return jsonify({
        'success': False,
        'message': 'Geocoding service not configured. Please enter coordinates manually.'
    })


# AI-GENERATED [2024-12-01]
# CRITICAL: Crisis routes must NEVER require authentication
# @see services.mental_health_resources_service for search logic 