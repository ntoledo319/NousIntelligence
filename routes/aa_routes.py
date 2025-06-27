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

# The underlying implementation is in routes.aa_content