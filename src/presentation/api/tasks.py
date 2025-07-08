from flask import Blueprint, jsonify, request
from src.infrastructure.di_container import container
from utils.unified_auth import login_required, demo_allowed
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('/health')
def health():
    """Health check for tasks service"""
    return jsonify({'status': 'healthy', 'service': 'tasks'})

@tasks_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@tasks_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error in tasks: {error}")
    return jsonify({'error': 'Internal server error'}), 500
