"""
Shopping API routes.
Handles shopping-related functionality such as shopping lists, products, etc.

@module shopping
@context_boundary Shopping Management
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import logging
from models import db, ShoppingList, ShoppingItem, Product
from utils.security_helper import rate_limit

# Create blueprint
shopping_bp = Blueprint('shopping_api', __name__, url_prefix='/api/shopping')

# Error handler for the blueprint
@shopping_bp.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions for this blueprint"""
    logging.error(f"Shopping API error: {str(e)}")
    return jsonify({
        'success': False,
        'error': str(e)
    }), 500

# Shopping List routes
@shopping_bp.route('/lists', methods=['GET'])
@login_required
def get_shopping_lists():
    """Get all shopping lists for the current user"""
    try:
        user_id = current_user.id
        shopping_lists = ShoppingList.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'shopping_lists': [sl.to_dict() for sl in shopping_lists]
        })
    except Exception as e:
        logging.error(f"Error fetching shopping lists: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/lists/<int:list_id>', methods=['GET'])
@login_required
def get_shopping_list(list_id):
    """Get a specific shopping list by ID"""
    try:
        user_id = current_user.id
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
        
        if not shopping_list:
            return jsonify({
                'success': False,
                'error': 'Shopping list not found'
            }), 404
            
        return jsonify({
            'success': True,
            'shopping_list': shopping_list.to_dict()
        })
    except Exception as e:
        logging.error(f"Error fetching shopping list: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/lists', methods=['POST'])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def create_shopping_list():
    """Create a new shopping list"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Validate required fields
        required_fields = ['name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Create new shopping list
        shopping_list = ShoppingList(
            name=data['name'],
            description=data.get('description', ''),
            store=data.get('store', ''),
            is_recurring=data.get('is_recurring', False),
            frequency_days=data.get('frequency_days', 0),
            user_id=current_user.id
        )
        
        # Add next_order_date if provided
        if 'next_order_date' in data:
            try:
                from datetime import datetime
                shopping_list.next_order_date = datetime.fromisoformat(
                    data['next_order_date'].replace('Z', '+00:00')
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid next_order_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
                
        db.session.add(shopping_list)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'shopping_list': shopping_list.to_dict(),
            'message': 'Shopping list created successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating shopping list: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/lists/<int:list_id>/items', methods=['GET'])
@login_required
def get_list_items(list_id):
    """Get all items in a shopping list"""
    try:
        user_id = current_user.id
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
        
        if not shopping_list:
            return jsonify({
                'success': False,
                'error': 'Shopping list not found'
            }), 404
            
        items = ShoppingItem.query.filter_by(shopping_list_id=list_id).all()
        
        return jsonify({
            'success': True,
            'items': [item.to_dict() for item in items],
            'list_name': shopping_list.name
        })
    except Exception as e:
        logging.error(f"Error fetching list items: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/lists/<int:list_id>/items', methods=['POST'])
@login_required
@rate_limit(max_requests=30, time_window=60)  # 30 requests per minute
def add_list_item(list_id):
    """Add a new item to a shopping list"""
    try:
        user_id = current_user.id
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
        
        if not shopping_list:
            return jsonify({
                'success': False,
                'error': 'Shopping list not found'
            }), 404
            
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Validate required fields
        required_fields = ['name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Create new shopping item
        item = ShoppingItem(
            shopping_list_id=list_id,
            name=data['name'],
            category=data.get('category', ''),
            quantity=data.get('quantity', 1),
            unit=data.get('unit', ''),
            notes=data.get('notes', ''),
            is_checked=data.get('is_checked', False),
            priority=data.get('priority', 0)
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': item.to_dict(),
            'message': 'Item added successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding list item: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/items/<int:item_id>/check', methods=['PUT'])
@login_required
def toggle_item_checked(item_id):
    """Toggle item checked status"""
    try:
        # First verify that the item belongs to a list owned by the current user
        item = ShoppingItem.query.join(ShoppingList).filter(
            ShoppingItem.id == item_id,
            ShoppingList.user_id == current_user.id
        ).first()
        
        if not item:
            return jsonify({
                'success': False,
                'error': 'Item not found'
            }), 404
            
        # Toggle the checked status
        item.is_checked = not item.is_checked
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': item.to_dict(),
            'message': f'Item {"checked" if item.is_checked else "unchecked"}'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error toggling item checked status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
def remove_list_item(item_id):
    """Remove an item from a shopping list"""
    try:
        # First verify that the item belongs to a list owned by the current user
        item = ShoppingItem.query.join(ShoppingList).filter(
            ShoppingItem.id == item_id,
            ShoppingList.user_id == current_user.id
        ).first()
        
        if not item:
            return jsonify({
                'success': False,
                'error': 'Item not found'
            }), 404
            
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item removed successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error removing list item: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Product routes
@shopping_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Get all products for the current user"""
    try:
        user_id = current_user.id
        products = Product.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'products': [product.to_dict() for product in products]
        })
    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/products/<int:product_id>', methods=['GET'])
@login_required
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        user_id = current_user.id
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
            
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
    except Exception as e:
        logging.error(f"Error fetching product: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shopping_bp.route('/products', methods=['POST'])
@login_required
@rate_limit(max_requests=20, time_window=60)  # 20 requests per minute
def add_product():
    """Add a new product"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Validate required fields
        required_fields = ['name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
            
        # Create new product
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            url=data.get('url', ''),
            image_url=data.get('image_url', ''),
            price=data.get('price', 0.0),
            source=data.get('source', ''),
            is_recurring=data.get('is_recurring', False),
            frequency_days=data.get('frequency_days', 0),
            user_id=current_user.id
        )
        
        # Set dates if provided
        if 'next_order_date' in data:
            try:
                from datetime import datetime
                product.next_order_date = datetime.fromisoformat(
                    data['next_order_date'].replace('Z', '+00:00')
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid next_order_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
                
        if 'last_ordered' in data:
            try:
                from datetime import datetime
                product.last_ordered = datetime.fromisoformat(
                    data['last_ordered'].replace('Z', '+00:00')
                )
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid last_ordered format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'
                }), 400
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'product': product.to_dict(),
            'message': 'Product added successfully'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding product: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 