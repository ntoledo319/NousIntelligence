from flask import Blueprint, jsonify, request
from src.infrastructure.di_container import container
from utils.unified_auth import login_required, demo_allowed
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

mental_health_bp = Blueprint('mental_health', __name__, url_prefix='/api/mental_health')

@mental_health_bp.route('/health')
def health():
    """Health check for mental_health service"""
    return jsonify({'status': 'healthy', 'service': 'mental_health'})

@mental_health_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@mental_health_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error in mental_health: {error}")
    return jsonify({'error': 'Internal server error'}), 500
