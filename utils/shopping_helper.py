import datetime
import logging
from models import db, ShoppingList, ShoppingItem
from utils.doctor_appointment_helper import get_user_id_from_session

def get_shopping_lists(session):
    """Get all shopping lists for the current user"""
    user_id = get_user_id_from_session(session)
    return ShoppingList.query.filter_by(user_id=user_id).all()

def get_shopping_list_by_id(list_id, session):
    """Get a specific shopping list by ID"""
    user_id = get_user_id_from_session(session)
    return ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()

def get_shopping_list_by_name(name, session):
    """Get a shopping list by name (case-insensitive)"""
    user_id = get_user_id_from_session(session)
    return ShoppingList.query.filter(
        ShoppingList.name.ilike(f"%{name}%"),
        ShoppingList.user_id == user_id
    ).first()

def create_shopping_list(name, description=None, store=None, session=None):
    """Create a new shopping list"""
    try:
        user_id = get_user_id_from_session(session)
        
        shopping_list = ShoppingList(
            name=name,
            description=description,
            store=store,
            user_id=user_id
        )
        
        db.session.add(shopping_list)
        db.session.commit()
        return shopping_list
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating shopping list: {str(e)}")
        return None

def add_item_to_list(list_id, item_name, quantity=1, unit=None, category=None, notes=None, session=None):
    """Add an item to a shopping list"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the list exists and belongs to the user
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
        if not shopping_list:
            return None
            
        # Create the new item
        item = ShoppingItem(
            shopping_list_id=list_id,
            name=item_name,
            quantity=quantity,
            unit=unit,
            category=category,
            notes=notes,
            is_checked=False
        )
        
        db.session.add(item)
        db.session.commit()
        return item
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding item to shopping list: {str(e)}")
        return None

def get_items_in_list(list_id, session):
    """Get all items in a shopping list"""
    user_id = get_user_id_from_session(session)
    
    # Verify the list exists and belongs to the user
    shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
    if not shopping_list:
        return []
        
    return ShoppingItem.query.filter_by(shopping_list_id=list_id).all()

def toggle_item_checked(item_id, is_checked, session):
    """Mark an item as checked or unchecked"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Get the item and verify it belongs to the user
        item = ShoppingItem.query.join(ShoppingList).filter(
            ShoppingItem.id == item_id,
            ShoppingList.user_id == user_id
        ).first()
        
        if not item:
            return None
            
        item.is_checked = is_checked
        db.session.commit()
        return item
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating item: {str(e)}")
        return None

def remove_item_from_list(item_id, session):
    """Remove an item from a shopping list"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Get the item and verify it belongs to the user
        item = ShoppingItem.query.join(ShoppingList).filter(
            ShoppingItem.id == item_id,
            ShoppingList.user_id == user_id
        ).first()
        
        if not item:
            return False
            
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error removing item: {str(e)}")
        return False

def set_list_as_recurring(list_id, frequency_days, session):
    """Set a shopping list as recurring with a frequency in days"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the list exists and belongs to the user
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
        if not shopping_list:
            return None
            
        shopping_list.is_recurring = True
        shopping_list.frequency_days = frequency_days
        shopping_list.next_order_date = datetime.datetime.now() + datetime.timedelta(days=frequency_days)
        
        db.session.commit()
        return shopping_list
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error setting list as recurring: {str(e)}")
        return None

def mark_list_as_ordered(list_id, session):
    """Mark a shopping list as ordered and update next order date if recurring"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the list exists and belongs to the user
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
        if not shopping_list:
            return None
            
        now = datetime.datetime.now()
        shopping_list.last_ordered = now
        
        # If this is a recurring list, calculate the next order date
        if shopping_list.is_recurring and shopping_list.frequency_days > 0:
            shopping_list.next_order_date = now + datetime.timedelta(days=shopping_list.frequency_days)
            
        # Mark all items as unchecked for the next round
        for item in shopping_list.items:
            item.is_checked = False
            
        db.session.commit()
        return shopping_list
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error marking list as ordered: {str(e)}")
        return None

def get_due_shopping_lists(session):
    """Get recurring shopping lists that are due for ordering"""
    user_id = get_user_id_from_session(session)
    now = datetime.datetime.now()
    
    return ShoppingList.query.filter(
        ShoppingList.user_id == user_id,
        ShoppingList.is_recurring == True,
        ShoppingList.next_order_date <= now
    ).all()