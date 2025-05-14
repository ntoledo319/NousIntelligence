import datetime
import logging
from models import db, Trip, ItineraryItem, Accommodation, TravelDocument, PackingItem
from utils.doctor_appointment_helper import get_user_id_from_session

# Trip management functions
def get_trips(session, include_past=False):
    """Get all trips for the current user"""
    user_id = get_user_id_from_session(session)
    query = Trip.query.filter_by(user_id=user_id)
    
    # Filter out past trips unless specifically requested
    if not include_past:
        today = datetime.datetime.now()
        query = query.filter(
            (Trip.end_date >= today) | (Trip.end_date.is_(None))
        )
        
    # Order by start date, soonest first
    return query.order_by(Trip.start_date).all()

def get_trip_by_id(trip_id, session):
    """Get a specific trip by ID"""
    user_id = get_user_id_from_session(session)
    return Trip.query.filter_by(id=trip_id, user_id=user_id).first()

def get_trip_by_name(name, session):
    """Get a trip by name (case-insensitive)"""
    user_id = get_user_id_from_session(session)
    return Trip.query.filter(
        Trip.name.ilike(f"%{name}%"),
        Trip.user_id == user_id
    ).first()

def create_trip(name, destination, start_date=None, end_date=None, budget=None, notes=None, session=None):
    """Create a new trip"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Validate dates
        if start_date and end_date and start_date > end_date:
            # Swap dates if end is before start
            start_date, end_date = end_date, start_date
            
        trip = Trip(
            name=name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            notes=notes,
            user_id=user_id
        )
        
        db.session.add(trip)
        db.session.commit()
        return trip
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating trip: {str(e)}")
        return None

def update_trip(trip_id, name=None, destination=None, start_date=None, end_date=None, 
                budget=None, notes=None, session=None):
    """Update a trip"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the trip exists and belongs to the user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
            
        # Update fields if provided
        if name:
            trip.name = name
        if destination:
            trip.destination = destination
        if start_date:
            trip.start_date = start_date
        if end_date:
            trip.end_date = end_date
        if budget is not None:
            trip.budget = budget
        if notes:
            trip.notes = notes
            
        # Validate dates
        if trip.start_date and trip.end_date and trip.start_date > trip.end_date:
            # Swap dates if end is before start
            trip.start_date, trip.end_date = trip.end_date, trip.start_date
            
        db.session.commit()
        return trip
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating trip: {str(e)}")
        return None

def delete_trip(trip_id, session):
    """Delete a trip"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the trip exists and belongs to the user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return False
            
        db.session.delete(trip)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting trip: {str(e)}")
        return False

def get_trip_cost(trip_id, session):
    """Calculate the total cost of a trip"""
    user_id = get_user_id_from_session(session)
    
    # Verify the trip exists and belongs to the user
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return None
        
    # Sum costs from itinerary items
    itinerary_cost = db.session.query(db.func.sum(ItineraryItem.cost)).filter(
        ItineraryItem.trip_id == trip_id,
        ItineraryItem.cost.isnot(None)
    ).scalar() or 0
    
    # Sum costs from accommodations
    accommodation_cost = db.session.query(db.func.sum(Accommodation.cost)).filter(
        Accommodation.trip_id == trip_id,
        Accommodation.cost.isnot(None)
    ).scalar() or 0
    
    # Sum costs from travel documents
    document_cost = db.session.query(db.func.sum(TravelDocument.cost)).filter(
        TravelDocument.trip_id == trip_id,
        TravelDocument.cost.isnot(None)
    ).scalar() or 0
    
    total_cost = itinerary_cost + accommodation_cost + document_cost
    
    return {
        'itinerary_cost': itinerary_cost,
        'accommodation_cost': accommodation_cost,
        'document_cost': document_cost,
        'total_cost': total_cost,
        'budget': trip.budget,
        'remaining': trip.budget - total_cost if trip.budget else None
    }

def get_upcoming_trips(session, days=30):
    """Get trips starting in the next X days"""
    user_id = get_user_id_from_session(session)
    today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=days)
    
    return Trip.query.filter(
        Trip.user_id == user_id,
        Trip.start_date.isnot(None),
        Trip.start_date >= today,
        Trip.start_date <= end_date
    ).order_by(Trip.start_date).all()

def get_active_trip(session):
    """Get currently active trip (if any)"""
    user_id = get_user_id_from_session(session)
    today = datetime.datetime.now()
    
    return Trip.query.filter(
        Trip.user_id == user_id,
        Trip.start_date <= today,
        (Trip.end_date >= today) | (Trip.end_date.is_(None))
    ).first()

# Itinerary management functions
def get_itinerary(trip_id, session):
    """Get all itinerary items for a trip"""
    user_id = get_user_id_from_session(session)
    
    # Verify the trip exists and belongs to the user
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return []
        
    # Get all itinerary items, ordered by date and time
    return ItineraryItem.query.filter_by(trip_id=trip_id).order_by(
        ItineraryItem.date, ItineraryItem.start_time
    ).all()

def get_itinerary_by_day(trip_id, date, session):
    """Get itinerary items for a specific day of a trip"""
    user_id = get_user_id_from_session(session)
    
    # Verify the trip exists and belongs to the user
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return []
        
    # Convert date to datetime range for the whole day
    day_start = datetime.datetime.combine(date, datetime.time.min)
    day_end = datetime.datetime.combine(date, datetime.time.max)
    
    # Get all itinerary items for this day, ordered by time
    return ItineraryItem.query.filter(
        ItineraryItem.trip_id == trip_id,
        ItineraryItem.date >= day_start,
        ItineraryItem.date <= day_end
    ).order_by(ItineraryItem.start_time).all()

def add_itinerary_item(trip_id, name, date=None, start_time=None, end_time=None, 
                       location=None, address=None, category=None, cost=None, 
                       reservation_confirmation=None, notes=None, session=None):
    """Add an item to a trip itinerary"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the trip exists and belongs to the user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
        
        # Create the itinerary item
        item = ItineraryItem(
            trip_id=trip_id,
            name=name,
            date=date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            address=address,
            category=category,
            cost=cost,
            reservation_confirmation=reservation_confirmation,
            notes=notes
        )
        
        db.session.add(item)
        db.session.commit()
        return item
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding itinerary item: {str(e)}")
        return None

def update_itinerary_item(item_id, name=None, date=None, start_time=None, end_time=None, 
                          location=None, address=None, category=None, cost=None, 
                          reservation_confirmation=None, notes=None, session=None):
    """Update an itinerary item"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the item exists and belongs to the user's trip
        item = (
            ItineraryItem.query
            .join(Trip)
            .filter(
                ItineraryItem.id == item_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not item:
            return None
            
        # Update fields if provided
        if name:
            item.name = name
        if date:
            item.date = date
        if start_time:
            item.start_time = start_time
        if end_time:
            item.end_time = end_time
        if location:
            item.location = location
        if address:
            item.address = address
        if category:
            item.category = category
        if cost is not None:
            item.cost = cost
        if reservation_confirmation:
            item.reservation_confirmation = reservation_confirmation
        if notes:
            item.notes = notes
            
        db.session.commit()
        return item
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating itinerary item: {str(e)}")
        return None

def delete_itinerary_item(item_id, session):
    """Delete an itinerary item"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the item exists and belongs to the user's trip
        item = (
            ItineraryItem.query
            .join(Trip)
            .filter(
                ItineraryItem.id == item_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not item:
            return False
            
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting itinerary item: {str(e)}")
        return False

# Accommodation management functions
def get_accommodations(trip_id, session):
    """Get all accommodations for a trip"""
    user_id = get_user_id_from_session(session)
    
    # Verify the trip exists and belongs to the user
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return []
        
    # Get all accommodations, ordered by check-in date
    return Accommodation.query.filter_by(trip_id=trip_id).order_by(
        Accommodation.check_in_date
    ).all()

def add_accommodation(trip_id, name, check_in_date=None, check_out_date=None, 
                     address=None, booking_confirmation=None, booking_site=None, 
                     phone=None, cost=None, notes=None, session=None):
    """Add an accommodation to a trip"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the trip exists and belongs to the user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
        
        # Create the accommodation
        accommodation = Accommodation(
            trip_id=trip_id,
            name=name,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            address=address,
            booking_confirmation=booking_confirmation,
            booking_site=booking_site,
            phone=phone,
            cost=cost,
            notes=notes
        )
        
        db.session.add(accommodation)
        db.session.commit()
        return accommodation
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding accommodation: {str(e)}")
        return None

def update_accommodation(accommodation_id, name=None, check_in_date=None, check_out_date=None,
                        address=None, booking_confirmation=None, booking_site=None,
                        phone=None, cost=None, notes=None, session=None):
    """Update an accommodation"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the accommodation exists and belongs to the user's trip
        accommodation = (
            Accommodation.query
            .join(Trip)
            .filter(
                Accommodation.id == accommodation_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not accommodation:
            return None
            
        # Update fields if provided
        if name:
            accommodation.name = name
        if check_in_date:
            accommodation.check_in_date = check_in_date
        if check_out_date:
            accommodation.check_out_date = check_out_date
        if address:
            accommodation.address = address
        if booking_confirmation:
            accommodation.booking_confirmation = booking_confirmation
        if booking_site:
            accommodation.booking_site = booking_site
        if phone:
            accommodation.phone = phone
        if cost is not None:
            accommodation.cost = cost
        if notes:
            accommodation.notes = notes
            
        db.session.commit()
        return accommodation
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating accommodation: {str(e)}")
        return None

def delete_accommodation(accommodation_id, session):
    """Delete an accommodation"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the accommodation exists and belongs to the user's trip
        accommodation = (
            Accommodation.query
            .join(Trip)
            .filter(
                Accommodation.id == accommodation_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not accommodation:
            return False
            
        db.session.delete(accommodation)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting accommodation: {str(e)}")
        return False

# Travel document management functions
def get_travel_documents(trip_id, session):
    """Get all travel documents for a trip"""
    user_id = get_user_id_from_session(session)
    
    # Verify the trip exists and belongs to the user
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return []
        
    # Get all travel documents, ordered by departure time
    return TravelDocument.query.filter_by(trip_id=trip_id).order_by(
        TravelDocument.departure_time
    ).all()

def add_travel_document(trip_id, name, document_type=None, confirmation_number=None,
                       provider=None, departure_location=None, arrival_location=None,
                       departure_time=None, arrival_time=None, cost=None, notes=None, session=None):
    """Add a travel document to a trip"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the trip exists and belongs to the user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
        
        # Create the travel document
        document = TravelDocument(
            trip_id=trip_id,
            name=name,
            document_type=document_type,
            confirmation_number=confirmation_number,
            provider=provider,
            departure_location=departure_location,
            arrival_location=arrival_location,
            departure_time=departure_time,
            arrival_time=arrival_time,
            cost=cost,
            notes=notes
        )
        
        db.session.add(document)
        db.session.commit()
        return document
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding travel document: {str(e)}")
        return None

def update_travel_document(document_id, name=None, document_type=None, confirmation_number=None,
                          provider=None, departure_location=None, arrival_location=None,
                          departure_time=None, arrival_time=None, cost=None, notes=None, session=None):
    """Update a travel document"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the document exists and belongs to the user's trip
        document = (
            TravelDocument.query
            .join(Trip)
            .filter(
                TravelDocument.id == document_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not document:
            return None
            
        # Update fields if provided
        if name:
            document.name = name
        if document_type:
            document.document_type = document_type
        if confirmation_number:
            document.confirmation_number = confirmation_number
        if provider:
            document.provider = provider
        if departure_location:
            document.departure_location = departure_location
        if arrival_location:
            document.arrival_location = arrival_location
        if departure_time:
            document.departure_time = departure_time
        if arrival_time:
            document.arrival_time = arrival_time
        if cost is not None:
            document.cost = cost
        if notes:
            document.notes = notes
            
        db.session.commit()
        return document
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating travel document: {str(e)}")
        return None

def delete_travel_document(document_id, session):
    """Delete a travel document"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the document exists and belongs to the user's trip
        document = (
            TravelDocument.query
            .join(Trip)
            .filter(
                TravelDocument.id == document_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not document:
            return False
            
        db.session.delete(document)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting travel document: {str(e)}")
        return False

# Packing list management functions
def get_packing_list(trip_id, session):
    """Get all packing items for a trip"""
    user_id = get_user_id_from_session(session)
    
    # Verify the trip exists and belongs to the user
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return []
        
    # Get all packing items, ordered by category
    return PackingItem.query.filter_by(trip_id=trip_id).order_by(
        PackingItem.category, PackingItem.name
    ).all()

def get_packing_items_by_category(trip_id, session):
    """Get packing items organized by category"""
    items = get_packing_list(trip_id, session)
    
    # Group by category
    categories = {}
    for item in items:
        category = item.category or "Uncategorized"
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
        
    return categories

def add_packing_item(trip_id, name, category=None, quantity=1, notes=None, session=None):
    """Add an item to a trip packing list"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the trip exists and belongs to the user
        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return None
        
        # Create the packing item
        item = PackingItem(
            trip_id=trip_id,
            name=name,
            category=category,
            quantity=quantity,
            is_packed=False,
            notes=notes
        )
        
        db.session.add(item)
        db.session.commit()
        return item
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding packing item: {str(e)}")
        return None

def update_packing_item(item_id, name=None, category=None, quantity=None, is_packed=None, notes=None, session=None):
    """Update a packing item"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the item exists and belongs to the user's trip
        item = (
            PackingItem.query
            .join(Trip)
            .filter(
                PackingItem.id == item_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not item:
            return None
            
        # Update fields if provided
        if name:
            item.name = name
        if category:
            item.category = category
        if quantity is not None:
            item.quantity = quantity
        if is_packed is not None:
            item.is_packed = is_packed
        if notes:
            item.notes = notes
            
        db.session.commit()
        return item
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating packing item: {str(e)}")
        return None

def toggle_packed_status(item_id, session):
    """Toggle the packed status of a packing item"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the item exists and belongs to the user's trip
        item = (
            PackingItem.query
            .join(Trip)
            .filter(
                PackingItem.id == item_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not item:
            return None
            
        # Toggle packed status
        item.is_packed = not item.is_packed
        db.session.commit()
        return item
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error toggling packed status: {str(e)}")
        return None

def delete_packing_item(item_id, session):
    """Delete a packing item"""
    try:
        user_id = get_user_id_from_session(session)
        
        # Verify the item exists and belongs to the user's trip
        item = (
            PackingItem.query
            .join(Trip)
            .filter(
                PackingItem.id == item_id,
                Trip.user_id == user_id
            )
            .first()
        )
        
        if not item:
            return False
            
        db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting packing item: {str(e)}")
        return False

def generate_standard_packing_list(trip_id, session=None):
    """Generate a standard packing list for a trip"""
    # Standard categories and items
    standard_items = {
        "Clothing": [
            "T-shirts", "Underwear", "Socks", "Pants/Shorts", 
            "Pajamas", "Sweater/jacket", "Comfortable shoes"
        ],
        "Toiletries": [
            "Toothbrush", "Toothpaste", "Shampoo", "Conditioner", 
            "Soap", "Deodorant", "Razor", "Sunscreen"
        ],
        "Electronics": [
            "Phone charger", "Camera", "Headphones", "Power adapter"
        ],
        "Documents": [
            "Passport/ID", "Travel insurance", "Boarding passes"
        ],
        "Essentials": [
            "Wallet", "Keys", "Medications", "Sunglasses"
        ]
    }
    
    # Add all standard items
    added_items = []
    for category, items in standard_items.items():
        for item_name in items:
            item = add_packing_item(trip_id, item_name, category, session=session)
            if item:
                added_items.append(item)
                
    return added_items

def get_packing_progress(trip_id, session):
    """Get packing progress statistics"""
    user_id = get_user_id_from_session(session)
    
    # Verify the trip exists and belongs to the user
    trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        return None
        
    # Count total and packed items
    total_items = PackingItem.query.filter_by(trip_id=trip_id).count()
    packed_items = PackingItem.query.filter_by(trip_id=trip_id, is_packed=True).count()
    
    # Calculate percentages
    percent_packed = (packed_items / total_items * 100) if total_items > 0 else 0
    
    return {
        'total_items': total_items,
        'packed_items': packed_items,
        'remaining_items': total_items - packed_items,
        'percent_packed': percent_packed
    }