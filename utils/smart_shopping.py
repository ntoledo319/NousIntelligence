"""
Smart shopping list generation and management
Uses AI to generate and organize shopping lists based on user's needs
"""

import os
import json
import logging
import datetime
from datetime import datetime, timedelta

# Import OpenAI for generating personalized lists
from openai import OpenAI

# Import models for accessing user data
from models import db, ShoppingList, ShoppingItem, Medication, Product

# Constants
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_smart_shopping_list(user_id, preferences=None):
    """
    Generate a smart shopping list based on user data and preferences
    
    Args:
        user_id: User identifier
        preferences: Optional dictionary with preferences
            - dietary_restrictions: List of restrictions (vegetarian, gluten-free, etc.)
            - favorite_stores: List of preferred stores
            - meal_type: Type of meals to include (breakfast, lunch, dinner, all)
            - days: Number of days to plan for
            - budget_level: Budget constraint (low, medium, high)
            
    Returns:
        Dictionary with generated list including items and metadata
    """
    try:
        if not OPENAI_API_KEY:
            return {"error": "OpenAI API key not configured"}
            
        # Set defaults for preferences
        if not preferences:
            preferences = {}
            
        dietary = preferences.get('dietary_restrictions', [])
        stores = preferences.get('favorite_stores', [])
        meal_type = preferences.get('meal_type', 'all')
        days = preferences.get('days', 7)
        budget = preferences.get('budget_level', 'medium')
        
        # Check if user has medications that need refilling
        medications_to_refill = []
        try:
            meds_query = Medication.query.filter_by(user_id=user_id)
            for med in meds_query.all():
                # Check if medication is low on quantity
                if med.remaining_quantity <= med.refill_threshold:
                    medications_to_refill.append({
                        'name': med.name,
                        'dosage': med.dosage,
                        'refill_amount': med.refill_amount
                    })
        except Exception as e:
            logging.error(f"Error checking medications: {str(e)}")
            
        # Check if user has recurring products that need ordering
        products_to_order = []
        try:
            now = datetime.utcnow()
            products_query = Product.query.filter_by(
                user_id=user_id,
                is_recurring=True
            ).filter(
                (Product.next_order_date <= now) | 
                (Product.next_order_date == None)
            )
            
            for product in products_query.all():
                products_to_order.append({
                    'name': product.name,
                    'source': product.source
                })
        except Exception as e:
            logging.error(f"Error checking products: {str(e)}")
            
        # Construct a prompt for the AI
        prompt = f"""
        Create a smart shopping list for a person with the following preferences:
        - Dietary restrictions: {', '.join(dietary) if dietary else 'None'}
        - Meal types to include: {meal_type}
        - Planning for {days} days of meals
        - Budget level: {budget}
        - Preferred stores: {', '.join(stores) if stores else 'Any'}
        
        The person also needs to refill these medications:
        {json.dumps(medications_to_refill) if medications_to_refill else "None"}
        
        And order these recurring products:
        {json.dumps(products_to_order) if products_to_order else "None"}
        
        Please organize the list by category (produce, dairy, meat, pantry, etc.) 
        and include estimated prices if possible.
        
        Format your response as a JSON object with these fields:
        1. "name": A descriptive name for the list
        2. "categories": Array of categories, each with "name" and "items" array
        3. "items": Array of all items with "name", "category", "estimated_price" (optional)
        4. "total_estimated_cost": Estimated total cost
        5. "suggested_store": Suggested store based on preferences
        """
        
        # Generate the shopping list using AI
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a helpful shopping assistant that creates organized shopping lists."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
            )
            
            # Parse the AI response
            try:
                content = response.choices[0].message.content
                if content is None:
                    return {"error": "Empty response from AI"}
                result = json.loads(content)
                return result
            except (json.JSONDecodeError, AttributeError) as e:
                logging.error(f"Error parsing AI response: {str(e)}")
                return {"error": "Could not parse AI response"}
                
        except Exception as e:
            logging.error(f"Error generating shopping list with AI: {str(e)}")
            return {"error": f"AI service error: {str(e)}"}
            
    except Exception as e:
        logging.error(f"Error generating smart shopping list: {str(e)}")
        return {"error": str(e)}

def save_smart_shopping_list(user_id, list_data):
    """
    Save a generated smart shopping list to the database
    
    Args:
        user_id: User identifier
        list_data: Dictionary with list data from generate_smart_shopping_list()
        
    Returns:
        Dictionary with saved list ID and success flag
    """
    try:
        # Create a new shopping list
        new_list = ShoppingList()
        new_list.name = list_data.get('name', 'Smart Shopping List')
        new_list.description = f"AI-generated list with {len(list_data.get('items', []))} items"
        new_list.store = list_data.get('suggested_store', '')
        new_list.user_id = user_id
        new_list.created_at = datetime.utcnow()
        
        db.session.add(new_list)
        db.session.flush()  # Get the new list ID without committing
        
        # Add all items to the list
        for item_data in list_data.get('items', []):
            item = ShoppingItem()
            item.name = item_data.get('name', '')
            item.category = item_data.get('category', '')
            item.notes = f"Est. price: ${item_data.get('estimated_price', 0)}"
            item.shopping_list_id = new_list.id
            item.is_checked = False
            db.session.add(item)
            
        # Commit all changes
        db.session.commit()
        
        return {
            'id': new_list.id,
            'success': True
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving smart shopping list: {str(e)}")
        return {"error": str(e)}

def generate_medication_shopping_list(user_id):
    """
    Generate a shopping list specifically for medications that need refilling
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with created list ID and success flag
    """
    try:
        # Check if user has medications that need refilling
        medications_to_refill = []
        
        meds_query = Medication.query.filter_by(user_id=user_id)
        for med in meds_query.all():
            # Check if medication is low on quantity
            if med.remaining_quantity <= med.refill_threshold:
                medications_to_refill.append({
                    'name': med.name,
                    'dosage': med.dosage,
                    'refill_amount': med.refill_amount
                })
                
        if not medications_to_refill:
            return {"message": "No medications need refilling", "success": False}
            
        # Create a new shopping list
        new_list = ShoppingList()
        new_list.name = "Medication Refills"
        new_list.description = f"Medications that need refilling ({len(medications_to_refill)} items)"
        new_list.store = "Pharmacy"
        new_list.user_id = user_id
        new_list.created_at = datetime.utcnow()
        
        db.session.add(new_list)
        db.session.flush()  # Get the new list ID without committing
        
        # Add all medications to the list
        for med_data in medications_to_refill:
            item = ShoppingItem()
            # Use dictionary access with get() method to handle potential KeyError
            item.name = f"{med_data.get('name', '')} ({med_data.get('dosage', '')})"
            item.category = "Medication"
            item.notes = f"Refill amount: {med_data.get('refill_amount', '')}"
            item.shopping_list_id = new_list.id
            item.is_checked = False
            db.session.add(item)
            
        # Commit all changes
        db.session.commit()
        
        return {
            'id': new_list.id,
            'success': True
        }
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error generating medication shopping list: {str(e)}")
        return {"error": str(e)}

def analyze_shopping_patterns(user_id):
    """
    Analyze user's shopping patterns to provide insights
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with insights about shopping patterns
    """
    try:
        # Get all shopping lists for this user
        lists_query = ShoppingList.query.filter_by(user_id=user_id)
        
        if lists_query.count() < 3:
            return {"message": "Not enough shopping history to analyze patterns", "success": False}
            
        # Collect all items across all lists
        all_items = []
        
        for shopping_list in lists_query.all():
            list_items = ShoppingItem.query.filter_by(shopping_list_id=shopping_list.id).all()
            
            for item in list_items:
                all_items.append({
                    'name': item.name,
                    'category': item.category,
                    'is_checked': item.is_checked,
                    'list_date': shopping_list.created_at,
                    'list_name': shopping_list.name
                })
                
        if not all_items:
            return {"message": "No shopping items found in history", "success": False}
            
        # Find frequently purchased items (appearing in multiple lists)
        item_frequency = {}
        
        for item in all_items:
            item_name = item['name'].lower()
            if item_name in item_frequency:
                item_frequency[item_name]['count'] += 1
                item_frequency[item_name]['lists'].add(item['list_name'])
            else:
                item_frequency[item_name] = {
                    'count': 1,
                    'category': item['category'],
                    'lists': {item['list_name']}
                }
                
        # Find frequently purchased items (3+ occurrences)
        frequent_items = []
        
        for name, data in item_frequency.items():
            if data['count'] >= 3:
                frequent_items.append({
                    'name': name,
                    'category': data['category'],
                    'count': data['count']
                })
                
        # Sort by frequency
        frequent_items.sort(key=lambda x: x['count'], reverse=True)
        
        # Find most common categories
        category_counts = {}
        
        for item in all_items:
            category = item['category'] or 'Uncategorized'
            category_counts[category] = category_counts.get(category, 0) + 1
            
        # Sort categories by count
        sorted_categories = sorted(
            [{'name': cat, 'count': count} for cat, count in category_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )
        
        # Calculate average list size
        list_sizes = {}
        
        for item in all_items:
            list_name = item['list_name']
            list_sizes[list_name] = list_sizes.get(list_name, 0) + 1
            
        avg_list_size = sum(list_sizes.values()) / len(list_sizes) if list_sizes else 0
        
        return {
            'frequent_items': frequent_items[:10],  # Top 10 frequent items
            'top_categories': sorted_categories[:5],  # Top 5 categories
            'average_list_size': round(avg_list_size, 1),
            'total_lists': len(list_sizes),
            'total_items': len(all_items),
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error analyzing shopping patterns: {str(e)}")
        return {"error": str(e)}

def suggest_list_improvements(user_id, list_id):
    """
    Suggest improvements for an existing shopping list
    
    Args:
        user_id: User identifier
        list_id: ID of the shopping list to improve
        
    Returns:
        Dictionary with suggested improvements
    """
    try:
        # Get the specified shopping list
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=user_id).first()
        
        if not shopping_list:
            return {"error": "Shopping list not found"}
            
        # Get items in the list
        list_items = ShoppingItem.query.filter_by(shopping_list_id=list_id).all()
        current_items = [{'name': item.name, 'category': item.category} for item in list_items]
        
        # Get statistics from past shopping
        shopping_patterns = analyze_shopping_patterns(user_id)
        
        # If no patterns are available, make basic suggestions
        if not shopping_patterns.get('success'):
            # Basic suggestions without history
            return {
                'suggested_additions': [],
                'organization_suggestions': "Consider organizing your list by store department for easier shopping.",
                'success': True
            }
            
        # Check for frequently purchased items missing from this list
        frequent_items = shopping_patterns.get('frequent_items', [])
        missing_frequent_items = []
        
        current_item_names = {item['name'].lower() for item in current_items}
        
        for freq_item in frequent_items:
            if freq_item['name'] not in current_item_names:
                missing_frequent_items.append(freq_item)
                
        # Analyze category organization
        categories_in_list = {}
        
        for item in current_items:
            category = item['category'] or 'Uncategorized'
            categories_in_list[category] = categories_in_list.get(category, 0) + 1
            
        # Check if items are properly categorized
        categorization_needed = len([item for item in current_items if not item['category']]) > 0
        
        # Return suggestions
        return {
            'suggested_additions': missing_frequent_items[:5],  # Top 5 suggestions
            'organization_suggestions': (
                "Consider categorizing uncategorized items for easier shopping" 
                if categorization_needed else 
                "Your list is well-organized by category"
            ),
            'missing_staples': missing_frequent_items[:5],
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error suggesting list improvements: {str(e)}")
        return {"error": str(e)}