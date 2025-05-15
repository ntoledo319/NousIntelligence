"""
Smart shopping list routes
All routes are prefixed with /smart-shopping
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user

# Import database models
from app import db
from models import ShoppingList, ShoppingItem

# Import smart shopping utils
from utils.smart_shopping import (
    generate_smart_shopping_list, 
    save_smart_shopping_list,
    generate_medication_shopping_list, 
    analyze_shopping_patterns,
    suggest_list_improvements
)

smart_shopping_bp = Blueprint('smart_shopping', __name__, url_prefix='/smart-shopping')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

@smart_shopping_bp.route('/')
@login_required
def index():
    """Smart shopping dashboard"""
    user_id = get_user_id()
    
    # Get user's existing shopping lists
    shopping_lists = ShoppingList.query.filter_by(user_id=user_id).order_by(ShoppingList.created_at.desc()).all()
    
    # Get shopping patterns if there's enough history
    shopping_patterns = analyze_shopping_patterns(user_id)
    
    return render_template(
        'smart_shopping/index.html',
        shopping_lists=shopping_lists,
        shopping_patterns=shopping_patterns
    )

@smart_shopping_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_list():
    """Generate a new smart shopping list"""
    user_id = get_user_id()
    
    if request.method == 'POST':
        # Get form data
        preferences = {
            'dietary_restrictions': request.form.getlist('dietary_restrictions'),
            'favorite_stores': [store.strip() for store in request.form.get('favorite_stores', '').split(',') if store.strip()],
            'meal_type': request.form.get('meal_type', 'all'),
            'days': int(request.form.get('days', 7)),
            'budget_level': request.form.get('budget_level', 'medium')
        }
        
        # Generate the smart list
        list_data = generate_smart_shopping_list(user_id, preferences)
        
        if list_data.get('error'):
            flash(f"Error generating list: {list_data.get('error')}", "error")
            return redirect(url_for('smart_shopping.generate_list'))
            
        # Save the generated list
        save_result = save_smart_shopping_list(user_id, list_data)
        
        if save_result.get('error'):
            flash(f"Error saving list: {save_result.get('error')}", "error")
            return redirect(url_for('smart_shopping.generate_list'))
            
        # Success! Redirect to the saved list
        flash("Smart shopping list generated successfully!", "success")
        return redirect(url_for('smart_shopping.view_list', list_id=save_result['id']))
    
    # GET request - show the form
    return render_template('smart_shopping/generate.html')

@smart_shopping_bp.route('/medication-list')
@login_required
def medication_list():
    """Generate a shopping list for medications that need refilling"""
    user_id = get_user_id()
    
    # Generate the medication list
    result = generate_medication_shopping_list(user_id)
    
    if result.get('error'):
        flash(f"Error generating medication list: {result.get('error')}", "error")
        return redirect(url_for('smart_shopping.index'))
        
    if not result.get('success'):
        flash(result.get('message', "No medications need refilling"), "info")
        return redirect(url_for('smart_shopping.index'))
        
    # Success! Redirect to the saved list
    flash("Medication shopping list generated successfully!", "success")
    return redirect(url_for('smart_shopping.view_list', list_id=result['id']))

@smart_shopping_bp.route('/list/<int:list_id>')
@login_required
def view_list(list_id):
    """View a specific shopping list"""
    user_id = get_user_id()
    
    # Get the shopping list
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    
    # Get items in the list
    list_items = ShoppingItem.query.filter_by(shopping_list_id=list_id).all()
    
    # Group items by category
    categorized_items = {}
    
    for item in list_items:
        category = item.category or 'Uncategorized'
        if category not in categorized_items:
            categorized_items[category] = []
        categorized_items[category].append(item)
        
    # Get suggested improvements
    improvement_suggestions = suggest_list_improvements(user_id, list_id)
    
    return render_template(
        'smart_shopping/view_list.html',
        shopping_list=shopping_list,
        categorized_items=categorized_items,
        suggestions=improvement_suggestions
    )

@smart_shopping_bp.route('/list/<int:list_id>/improve')
@login_required
def improve_list(list_id):
    """Apply suggested improvements to a shopping list"""
    user_id = get_user_id()
    
    # Get the shopping list
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    
    # Get suggested improvements
    improvement_suggestions = suggest_list_improvements(user_id, list_id)
    
    if improvement_suggestions.get('error'):
        flash(f"Error getting suggestions: {improvement_suggestions.get('error')}", "error")
        return redirect(url_for('smart_shopping.view_list', list_id=list_id))
        
    # Add suggested missing items to the list
    for item in improvement_suggestions.get('suggested_additions', []):
        # Check if item already exists
        existing = ShoppingItem.query.filter_by(
            shopping_list_id=list_id, 
            name=item['name']
        ).first()
        
        if not existing:
            new_item = ShoppingItem(
                name=item['name'],
                category=item['category'],
                notes="Added automatically based on shopping patterns",
                shopping_list_id=list_id,
                is_checked=False
            )
            db.session.add(new_item)
    
    db.session.commit()
    
    flash("Shopping list improved with suggested items!", "success")
    return redirect(url_for('smart_shopping.view_list', list_id=list_id))

@smart_shopping_bp.route('/list/<int:list_id>/toggle-item/<int:item_id>', methods=['POST'])
@login_required
def toggle_item(list_id, item_id):
    """Toggle an item's checked status"""
    user_id = get_user_id()
    
    # Verify the shopping list belongs to this user
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    
    # Get the item
    item = ShoppingItem.query.filter_by(id=item_id, shopping_list_id=list_id).first_or_404()
    
    # Toggle checked status
    item.is_checked = not item.is_checked
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        return jsonify({"success": True, "checked": item.is_checked})
    else:
        # Regular request
        return redirect(url_for('smart_shopping.view_list', list_id=list_id))

@smart_shopping_bp.route('/list/<int:list_id>/add-item', methods=['POST'])
@login_required
def add_item(list_id):
    """Add a new item to a shopping list"""
    user_id = get_user_id()
    
    # Verify the shopping list belongs to this user
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first_or_404()
    
    # Get form data
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not name:
        flash("Item name is required", "error")
        return redirect(url_for('smart_shopping.view_list', list_id=list_id))
        
    # Add the new item
    new_item = ShoppingItem(
        name=name,
        category=category,
        notes=notes,
        shopping_list_id=list_id,
        is_checked=False
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    flash("Item added successfully", "success")
    return redirect(url_for('smart_shopping.view_list', list_id=list_id))