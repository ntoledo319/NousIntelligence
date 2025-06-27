"""
AA Routes Module

This module defines routes for the AA (Alcoholics Anonymous) feature.
It serves as a wrapper around the detailed routes defined in aa_content.py.
"""

from flask import Blueprint, redirect, url_for

# Create the blueprint for AA routes
aa_bp = Blueprint('aa', __name__, url_prefix='/aa')

# Import and register aa_content module routes
from routes.aa_content import aa_content
aa_bp.register_blueprint(aa_content)

# Register API routes for AA content
from routes.api_routes import api
aa_bp.register_blueprint(api, url_prefix='/api')

@aa_bp.route('/')
def index():
    """Redirect to the main AA content page"""
    return redirect(url_for('aa.aa_content.index'))

# The underlying implementation is in routes.aa_content