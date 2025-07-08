from flask import Blueprint, jsonify, request
from src.infrastructure.di_container import container
from utils.unified_auth import login_required, demo_allowed
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/health')
def health():
    """Health check for auth service"""
    return jsonify({'status': 'healthy', 'service': 'auth'})

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error in auth: {error}")
    return jsonify({'error': 'Internal server error'}), 500
