"""
Price tracking routes
All routes are prefixed with /price-tracking
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user

# Import database models
from models import db, Product, PriceHistory, PriceAlert, Deal
from utils.price_tracking import (
    track_product, get_user_tracked_products, update_product_price,
    get_price_history, create_price_alert, find_seasonal_deals
)

price_tracking_bp = Blueprint('price_tracking', __name__, url_prefix='/price-tracking')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

@price_tracking_bp.route('/')
@login_required
def index():
    """Price tracking dashboard"""
    user_id = get_user_id()
    
    # Get user's tracked products
    tracked_products = get_user_tracked_products(user_id, limit=10)
    
    # Get seasonal deals
    seasonal_deals = find_seasonal_deals(user_id)
    
    # Get price alerts
    price_alerts = PriceAlert.query.filter_by(
        user_id=user_id, 
        is_active=True
    ).join(Product).all()
    
    return render_template(
        'price_tracking/index.html',
        tracked_products=tracked_products,
        seasonal_deals=seasonal_deals,
        price_alerts=price_alerts
    )

@price_tracking_bp.route('/track', methods=['GET', 'POST'])
@login_required
def track():
    """Track a new product"""
    user_id = get_user_id()
    
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        name = request.form.get('name', '').strip() or None
        description = request.form.get('description', '').strip() or None
        
        if not url:
            flash("Product URL is required", "error")
            return redirect(url_for('price_tracking.track'))
            
        # Track the product
        result = track_product(url, name, description, user_id)
        
        if isinstance(result, dict) and 'error' in result:
            flash(f"Error tracking product: {result['error']}", "error")
            return redirect(url_for('price_tracking.track'))
            
        flash("Product tracked successfully!", "success")
        return redirect(url_for('price_tracking.view_product', product_id=result.id))
    
    # GET request - show form
    return render_template('price_tracking/track.html')

@price_tracking_bp.route('/product/<int:product_id>')
@login_required
def view_product(product_id):
    """View a specific tracked product"""
    user_id = get_user_id()
    
    # Get the product
    product = Product.query.filter_by(id=product_id, user_id=user_id).first_or_404()
    
    # Get price history
    price_history_data = get_price_history(product_id, user_id)
    
    # Get price alerts for this product
    price_alerts = PriceAlert.query.filter_by(
        product_id=product_id,
        user_id=user_id,
        is_active=True
    ).all()
    
    # Check if this product is a good deal
    is_deal = False
    if price_history_data.get('average_price') and price_history_data.get('current_price'):
        avg_price = price_history_data.get('average_price')
        current_price = price_history_data.get('current_price')
        is_deal = current_price <= (avg_price * 0.9)
    
    return render_template(
        'price_tracking/view_product.html',
        product=product,
        price_history=price_history_data,
        price_alerts=price_alerts,
        is_deal=is_deal
    )

@price_tracking_bp.route('/product/<int:product_id>/update-price')
@login_required
def update_price(product_id):
    """Update a product's price"""
    user_id = get_user_id()
    
    # Update the price
    result = update_product_price(product_id, user_id)
    
    if isinstance(result, dict) and 'error' in result:
        flash(f"Error updating price: {result['error']}", "error")
    elif result.get('price_changed', False):
        flash("Price updated successfully!", "success")
    else:
        flash("Price checked but no change detected", "info")
        
    return redirect(url_for('price_tracking.view_product', product_id=product_id))

@price_tracking_bp.route('/product/<int:product_id>/create-alert', methods=['POST'])
@login_required
def create_alert(product_id):
    """Create a price alert for a product"""
    user_id = get_user_id()
    
    # Get alert parameters
    target_price = request.form.get('target_price')
    if target_price:
        try:
            target_price = float(target_price)
        except ValueError:
            target_price = None
    
    percentage_drop = request.form.get('percentage_drop')
    if percentage_drop:
        try:
            percentage_drop = float(percentage_drop)
        except ValueError:
            percentage_drop = None
    
    notification_method = request.form.get('notification_method', 'app')
    
    # Create the alert
    result = create_price_alert(
        product_id=product_id,
        user_id=user_id,
        target_price=target_price,
        percentage_drop=percentage_drop,
        notification_method=notification_method
    )
    
    if isinstance(result, dict) and 'error' in result:
        flash(f"Error creating alert: {result['error']}", "error")
    else:
        flash("Price alert created successfully!", "success")
        
    return redirect(url_for('price_tracking.view_product', product_id=product_id))

@price_tracking_bp.route('/product/<int:product_id>/delete-alert/<int:alert_id>', methods=['POST'])
@login_required
def delete_alert(product_id, alert_id):
    """Delete a price alert"""
    user_id = get_user_id()
    
    # Get the alert
    alert = PriceAlert.query.filter_by(
        id=alert_id,
        product_id=product_id,
        user_id=user_id
    ).first_or_404()
    
    # Delete the alert
    db.session.delete(alert)
    db.session.commit()
    
    flash("Price alert deleted successfully!", "success")
    return redirect(url_for('price_tracking.view_product', product_id=product_id))

@price_tracking_bp.route('/product/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete a tracked product"""
    user_id = get_user_id()
    
    # Get the product
    product = Product.query.filter_by(id=product_id, user_id=user_id).first_or_404()
    
    # Delete the product (cascade will delete price history and alerts)
    db.session.delete(product)
    db.session.commit()
    
    flash("Product tracking removed successfully!", "success")
    return redirect(url_for('price_tracking.index'))

@price_tracking_bp.route('/deals')
@login_required
def deals():
    """View current deals"""
    user_id = get_user_id()
    
    # Get all verified active deals
    active_deals = Deal.query.filter(
        Deal.is_verified == True,
        Deal.end_date >= datetime.utcnow()
    ).order_by(Deal.discount_percentage.desc()).limit(20).all()
    
    # Get seasonal deals
    seasonal_deals = find_seasonal_deals(user_id)
    
    # Get user-specific deals (based on tracked products)
    user_product_deals = []
    tracked_products = get_user_tracked_products(user_id)
    for product in tracked_products:
        if product.deals:
            for deal in product.deals:
                if deal.is_verified and (not deal.end_date or deal.end_date >= datetime.utcnow()):
                    user_product_deals.append(deal)
    
    return render_template(
        'price_tracking/deals.html',
        active_deals=active_deals,
        seasonal_deals=seasonal_deals,
        user_product_deals=user_product_deals
    )

@price_tracking_bp.route('/deals/add', methods=['GET', 'POST'])
@login_required
def add_deal():
    """Add a new deal"""
    user_id = get_user_id()
    
    if request.method == 'POST':
        # Get deal parameters
        name = request.form.get('name')
        description = request.form.get('description')
        url = request.form.get('url')
        source = request.form.get('source')
        
        original_price = request.form.get('original_price')
        if original_price:
            try:
                original_price = float(original_price)
            except ValueError:
                original_price = None
                
        deal_price = request.form.get('deal_price')
        if deal_price:
            try:
                deal_price = float(deal_price)
            except ValueError:
                deal_price = None
                
        # Calculate discount percentage
        discount_percentage = None
        if original_price and deal_price and original_price > 0:
            discount_percentage = ((original_price - deal_price) / original_price) * 100
            
        # Get product ID if provided
        product_id = request.form.get('product_id')
        if product_id:
            try:
                product_id = int(product_id)
                # Verify product belongs to user
                product = Product.query.filter_by(id=product_id, user_id=user_id).first()
                if not product:
                    product_id = None
            except ValueError:
                product_id = None
                
        # Create the deal
        deal = Deal(
            product_id=product_id,
            name=name,
            description=description,
            url=url,
            source=source,
            original_price=original_price,
            deal_price=deal_price,
            discount_percentage=discount_percentage,
            user_id=user_id,
            is_verified=False  # Deals added by users start as unverified
        )
        
        db.session.add(deal)
        db.session.commit()
        
        flash("Deal added successfully! It will be verified by a moderator.", "success")
        return redirect(url_for('price_tracking.deals'))
    
    # GET request - show form
    # Get user's tracked products for product selection
    tracked_products = get_user_tracked_products(user_id)
    
    return render_template(
        'price_tracking/add_deal.html',
        tracked_products=tracked_products
    )

@price_tracking_bp.route('/deals/<int:deal_id>/rate', methods=['POST'])
@login_required
def rate_deal(deal_id):
    """Rate a deal"""
    user_id = get_user_id()
    
    # Get the deal
    deal = Deal.query.filter_by(id=deal_id).first_or_404()
    
    # Get the rating
    rating = request.form.get('rating')
    if rating:
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                deal.rating = rating
                db.session.commit()
                flash("Deal rated successfully!", "success")
            else:
                flash("Rating must be between 1 and 5", "error")
        except ValueError:
            flash("Invalid rating", "error")
    else:
        flash("Rating is required", "error")
        
    return redirect(url_for('price_tracking.deals'))

# API endpoints for AJAX requests
@price_tracking_bp.route('/api/products', methods=['GET'])
@login_required
def api_get_products():
    """API endpoint to get tracked products"""
    user_id = get_user_id()
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    products = get_user_tracked_products(user_id, limit, offset)
    
    return jsonify({
        'success': True,
        'products': [product.to_dict() for product in products]
    })

@price_tracking_bp.route('/api/products/<int:product_id>/price-history', methods=['GET'])
@login_required
def api_get_price_history(product_id):
    """API endpoint to get price history for a product"""
    user_id = get_user_id()
    days = request.args.get('days', 30, type=int)
    
    price_history = get_price_history(product_id, user_id, days)
    
    return jsonify(price_history)

@price_tracking_bp.route('/api/products/<int:product_id>/update-price', methods=['POST'])
@login_required
def api_update_price(product_id):
    """API endpoint to update a product's price"""
    user_id = get_user_id()
    
    result = update_product_price(product_id, user_id)
    
    return jsonify(result) 