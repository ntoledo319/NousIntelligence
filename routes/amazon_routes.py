"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Amazon Routes Routes
Amazon Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

amazon_routes_bp = Blueprint('amazon_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Amazon shopping routes
All routes are prefixed with /amazon
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session

from werkzeug.utils import secure_filename

# Import database from the app
from app import db

# Import models
from models import Product, ShoppingList, ShoppingItem

# Import Amazon helper
from utils.amazon_helper import (
    search_amazon_products,
    get_product_details,
    create_amazon_tracking,
    format_amazon_affiliate_url
)

amazon_bp = Blueprint('amazon', __name__, url_prefix='/amazon')

# Helper to get user_id from session.get('user')
def get_user_id():
    return str(session.get('user', {}).get('id', 'demo_user')) if ('user' in session and session['user']) else None

# Amazon product search
@amazon_bp.route('/search')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def search():
    """Search for products on Amazon"""
    query = request.args.get('query', '')

    if not query:
        return render_template(
            'amazon/search.html',
            results=None,
            query=None
        )

    # Search for products
    results = search_amazon_products(query)

    # Check if we got an error
    if isinstance(results, dict) and 'error' in results:
        flash(f"Error searching for products: {results['error']}", "danger")
        results = []

    return render_template(
        'amazon/search.html',
        results=results,
        query=query
    )

# View product details
@amazon_bp.route('/product/<path:asin_or_url>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def product_details(asin_or_url):
    """View details for a specific product"""
    user_id = get_user_id()

    # Get product details
    product = get_product_details(asin_or_url)

    # Check if we got an error
    if isinstance(product, dict) and 'error' in product:
        flash(f"Error getting product details: {product['error']}", "danger")
        return redirect(url_for('amazon.search'))

    # Check if this product is already being tracked
    existing_product = None
    if 'url' in product:
        existing_product = Product.query.filter_by(
            user_id=user_id,
            url=product['url']
        ).first()

    # Get user's shopping lists for quick add
    shopping_lists = ShoppingList.query.filter_by(user_id=user_id).all()

    return render_template(
        'amazon/product.html',
        product=product,
        existing_product=existing_product,
        shopping_lists=shopping_lists
    )

# Track a product
@amazon_bp.route('/track', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def track_product():
    """Track a product for price changes and availability"""
    user_id = get_user_id()

    # Get form data
    product_url = request.form.get('product_url')
    is_recurring = request.form.get('is_recurring') == 'on'
    frequency_days = int(request.form.get('frequency_days', 30))

    if not product_url:
        flash("Missing product URL", "danger")
        return redirect(url_for('amazon.search'))

    # Get product details
    product_data = get_product_details(product_url)

    # Check if we got an error
    if isinstance(product_data, dict) and 'error' in product_data:
        flash(f"Error getting product details: {product_data['error']}", "danger")
        return redirect(url_for('amazon.search'))

    # Create product tracking
    product = create_amazon_tracking(
        user_id,
        product_data,
        is_recurring=is_recurring,
        frequency_days=frequency_days
    )

    if product:
        flash(f"Now tracking {product.name}", "success")

        # If recurring, also show next order date
        if is_recurring and product.next_order_date:
            flash(f"Next order scheduled for {product.next_order_date.strftime('%B %d, %Y')}", "info")
    else:
        flash("Error creating product tracking", "danger")

    # Redirect to product page
    return redirect(url_for('amazon.product_details', asin_or_url=product_url))

# Add product to shopping list
@amazon_bp.route('/add-to-list', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def add_to_shopping_list():
    """Add a product to a shopping list"""
    user_id = get_user_id()

    # Get form data
    product_name = request.form.get('product_name')
    product_price = request.form.get('product_price', '0')
    product_url = request.form.get('product_url')
    list_id = request.form.get('list_id')

    if not product_name or not list_id:
        flash("Missing product name or list ID", "danger")
        return redirect(request.referrer or url_for('amazon.search'))

    # Get the shopping list
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()

    if not shopping_list:
        flash("Shopping list not found", "danger")
        return redirect(request.referrer or url_for('amazon.search'))

    try:
        # Create a new shopping item
        item = ShoppingItem(
            shopping_list_id=shopping_list.id,
            name=product_name,
            category="Amazon",
            estimated_price=float(product_price) if product_price else None,
            notes=f"Amazon: {product_url}" if product_url else None
        )

        db.session.add(item)
        db.session.commit()

        flash(f"Added {product_name} to {shopping_list.name}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding item to list: {str(e)}", "danger")

    # Redirect back to the referring page
    return redirect(request.referrer or url_for('amazon.search'))

# Manage tracked products
@amazon_bp.route('/tracked')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def tracked_products():
    """View all tracked Amazon products"""
    user_id = get_user_id()

    # Get all tracked products from Amazon
    products = Product.query.filter_by(
        user_id=user_id,
        source='Amazon'
    ).order_by(Product.created_at.desc()).all()

    # Separate recurring and non-recurring products
    recurring_products = [p for p in products if p.is_recurring]
    one_time_products = [p for p in products if not p.is_recurring]

    return render_template(
        'amazon/tracked.html',
        recurring_products=recurring_products,
        one_time_products=one_time_products
    )

# Remove product tracking
@amazon_bp.route('/untrack/<int:product_id>', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def untrack_product(product_id):
    """Stop tracking a product"""
    user_id = get_user_id()

    # Get the product
    product = Product.query.filter_by(id=product_id, user_id=user_id).first()

    if not product:
        flash("Product not found", "danger")
        return redirect(url_for('amazon.tracked_products'))

    try:
        product_name = product.name
        db.session.delete(product)
        db.session.commit()

        flash(f"Stopped tracking {product_name}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error removing product tracking: {str(e)}", "danger")

    return redirect(url_for('amazon.tracked_products'))

# Mark product as ordered
@amazon_bp.route('/mark-ordered/<int:product_id>', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def mark_ordered(product_id):
    """Mark a product as ordered"""
    user_id = get_user_id()

    # Get the product
    product = Product.query.filter_by(id=product_id, user_id=user_id).first()

    if not product:
        flash("Product not found", "danger")
        return redirect(url_for('amazon.tracked_products'))

    try:
        from datetime import datetime, timedelta

        # Update the product
        product.last_ordered = datetime.utcnow()

        # If recurring, update next order date
        if product.is_recurring and product.frequency_days > 0:
            product.next_order_date = datetime.utcnow() + timedelta(days=product.frequency_days)

        db.session.commit()

        flash(f"Marked {product.name} as ordered", "success")

        # If recurring, also show next order date
        if product.is_recurring and product.next_order_date:
            flash(f"Next order scheduled for {product.next_order_date.strftime('%B %d, %Y')}", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating product: {str(e)}", "danger")

    return redirect(url_for('amazon.tracked_products'))