"""
Smart Shopping Routes

This module provides routes for smart shopping functionality.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

# Create blueprint
smart_shopping_bp = Blueprint('smart_shopping', __name__, url_prefix='/smart-shopping')

# Set up logger
logger = logging.getLogger(__name__)

@smart_shopping_bp.route('/')
def index():
    """Smart shopping homepage"""
    return render_template('smart_shopping/index.html')

@smart_shopping_bp.route('/recommendations')
def recommendations():
    """Product recommendations"""
    return render_template('smart_shopping/recommendations.html')

@smart_shopping_bp.route('/deals')
def deals():
    """Current deals and discounts"""
    return render_template('smart_shopping/deals.html')