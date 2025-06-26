import datetime
import logging
import re
import json
import requests
from models import db, Product
from utils.doctor_appointment_helper import get_user_id_from_session

def get_products(session):
    """Get all tracked products for the current user"""
    user_id = get_user_id_from_session(session)
    return Product.query.filter_by(user_id=user_id).all()

def get_product_by_id(product_id, session):
    """Get a specific product by ID"""
    user_id = get_user_id_from_session(session)
    return Product.query.filter_by(id=product_id, user_id=user_id).first()

def get_product_by_name(name, session):
    """Get a product by name (case-insensitive)"""
    user_id = get_user_id_from_session(session)
    return Product.query.filter(
        Product.name.ilike(f"%{name}%"),
        Product.user_id == user_id
    ).first()

def add_product(name, url=None, description=None, price=None, source=None, session=None):
    """Add a new product to track"""
    try:
        user_id = get_user_id_from_session(session)

        # If we have a URL, try to fetch product details
        image_url = None
        if url and not description:
            description, price, image_url = fetch_product_details(url)

        product = Product(
            name=name,
            url=url,
            description=description,
            price=price,
            image_url=image_url,
            source=source or extract_source_from_url(url) if url else None,
            user_id=user_id
        )

        db.session.add(product)
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding product: {str(e)}")
        return None

def extract_source_from_url(url):
    """Extract the source (e.g., Amazon, Target) from a product URL"""
    if not url:
        return None

    # Try to extract domain name
    domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if domain_match:
        domain = domain_match.group(1)
        # Extract the main part of the domain (e.g., amazon.com -> amazon)
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[-2].capitalize()  # Return the second-to-last part
    return None

def fetch_product_details(url):
    """
    Attempt to fetch basic product details from a URL

    Returns:
        tuple: (description, price, image_url)
    """
    # This is a placeholder function that would need more robust implementation
    # with libraries like BeautifulSoup to properly scrape product details
    # or integration with APIs like Amazon Product API

    try:
        # For demonstration purposes only - in real implementation,
        # this would use proper web scraping techniques
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None, None, None

        # This is a very simplified extraction - real implementation would be more robust
        html = response.text

        # Try to find a description
        description = None
        desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
        if desc_match:
            description = desc_match.group(1)

        # Try to find a price
        price = None
        price_match = re.search(r'\\$(\d+\.\d{2})', html)
        if price_match:
            try:
                price = float(price_match.group(1))
            except ValueError:
                pass

        # Try to find an image
        image_url = None
        img_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        if img_match:
            image_url = img_match.group(1)

        return description, price, image_url
    except Exception as e:
        logging.error(f"Error fetching product details: {str(e)}")
        return None, None, None

def set_product_as_recurring(product_id, frequency_days, session):
    """Set a product to be ordered on a recurring basis"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the product exists and belongs to the user
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if not product:
            return None

        product.is_recurring = True
        product.frequency_days = frequency_days
        product.next_order_date = datetime.datetime.now() + datetime.timedelta(days=frequency_days)

        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error setting product as recurring: {str(e)}")
        return None

def mark_product_as_ordered(product_id, session):
    """Mark a product as ordered and update next order date if recurring"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the product exists and belongs to the user
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if not product:
            return None

        now = datetime.datetime.now()
        product.last_ordered = now

        # If this is a recurring product, calculate the next order date
        if product.is_recurring and product.frequency_days > 0:
            product.next_order_date = now + datetime.timedelta(days=product.frequency_days)

        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error marking product as ordered: {str(e)}")
        return None

def get_due_product_orders(session):
    """Get recurring products that are due for ordering"""
    user_id = get_user_id_from_session(session)
    now = datetime.datetime.now()

    return Product.query.filter(
        Product.user_id == user_id,
        Product.is_recurring == True,
        Product.next_order_date <= now
    ).all()

def update_product_price(product_id, new_price, session):
    """Update the price of a tracked product"""
    try:
        user_id = get_user_id_from_session(session)

        # Verify the product exists and belongs to the user
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if not product:
            return None

        product.price = new_price
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating product price: {str(e)}")
        return None