"""
Price tracking and management utilities
Supports product price history tracking, price comparison, and alerts
"""

import re
import os
import json
import logging
import requests
import datetime
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from models import db, Product, PriceHistory, PriceAlert, Deal
from utils.shopping_helper import get_user_id_from_session

# Configure headers for web scraping
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, deflate, br',
}

def track_product(url, name=None, description=None, user_id=None):
    """
    Track a product by URL, scraping initial details and creating a record

    Args:
        url: URL to the product page
        name: Product name (optional, will be scraped if not provided)
        description: Product description (optional, will be scraped if not provided)
        user_id: User ID of the product tracker

    Returns:
        Tracked product object or error
    """
    try:
        # Check if product URL is already being tracked by this user
        existing_product = Product.query.filter_by(url=url, user_id=user_id).first()
        if existing_product:
            return existing_product

        # Determine the source from the URL
        source = extract_source_from_url(url)

        # Scrape product details if not provided
        if not name or not description:
            scraped_details = scrape_product_details(url)
            if 'error' in scraped_details:
                return {'error': scraped_details['error']}

            name = name or scraped_details.get('name')
            description = description or scraped_details.get('description')
            price = scraped_details.get('price')
            image_url = scraped_details.get('image_url')
        else:
            # If details provided, still get price for initial tracking
            scraped_price = scrape_product_price(url)
            price = scraped_price.get('price') if 'error' not in scraped_price else None
            image_url = None

        # Create new product
        product = Product(
            name=name,
            description=description,
            url=url,
            image_url=image_url,
            price=price,
            source=source,
            user_id=user_id,
            created_at=datetime.utcnow()
        )

        db.session.add(product)
        db.session.flush()  # Get ID without committing

        # Add initial price history
        if price:
            price_history = PriceHistory(
                product_id=product.id,
                price=price,
                date_recorded=datetime.utcnow(),
                source=source,
                is_deal=False
            )
            db.session.add(price_history)

        db.session.commit()
        return product

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error tracking product: {str(e)}")
        return {'error': str(e)}

def get_user_tracked_products(user_id, limit=50, offset=0):
    """
    Get tracked products for a specific user

    Args:
        user_id: User ID to get tracked products for
        limit: Maximum number of products to return
        offset: Offset for pagination

    Returns:
        List of tracked products
    """
    try:
        products = Product.query.filter_by(user_id=user_id).order_by(
            Product.created_at.desc()
        ).offset(offset).limit(limit).all()

        return products
    except Exception as e:
        logging.error(f"Error getting tracked products: {str(e)}")
        return []

def update_product_price(product_id, user_id=None):
    """
    Update a product's price by scraping current value

    Args:
        product_id: ID of the product to update
        user_id: User ID for authentication check (optional)

    Returns:
        Updated price info or error
    """
    try:
        # Get product details
        product_query = Product.query.filter_by(id=product_id)
        if user_id:
            product_query = product_query.filter_by(user_id=user_id)

        product = product_query.first()

        if not product:
            return {'error': 'Product not found'}

        # Scrape current price
        scraped_price = scrape_product_price(product.url)
        if 'error' in scraped_price:
            return scraped_price

        # Get current price
        current_price = scraped_price.get('price')
        if not current_price:
            return {'error': 'Failed to extract price'}

        # Check if price has changed
        price_changed = product.price != current_price

        # Update product price
        product.price = current_price
        product.updated_at = datetime.utcnow()

        # Add price history record if price changed
        if price_changed:
            price_history = PriceHistory(
                product_id=product.id,
                price=current_price,
                date_recorded=datetime.utcnow(),
                source=product.source,
                is_deal=is_likely_deal(product, current_price)
            )
            db.session.add(price_history)

            # Check if this triggers any price alerts
            check_price_alerts(product.id, current_price)

        db.session.commit()

        return {
            'product_id': product.id,
            'current_price': current_price,
            'price_changed': price_changed,
            'updated_at': product.updated_at.isoformat()
        }

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating product price: {str(e)}")
        return {'error': str(e)}

def get_price_history(product_id, user_id=None, days=30):
    """
    Get price history for a specific product

    Args:
        product_id: ID of the product
        user_id: User ID for authentication check (optional)
        days: Number of days to get history for

    Returns:
        Price history data
    """
    try:
        # First ensure user has access to this product
        product_query = Product.query.filter_by(id=product_id)
        if user_id:
            product_query = product_query.filter_by(user_id=user_id)

        product = product_query.first()

        if not product:
            return {'error': 'Product not found or access denied'}

        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get price history
        price_history = PriceHistory.query.filter(
            PriceHistory.product_id == product_id,
            PriceHistory.date_recorded >= cutoff_date
        ).order_by(PriceHistory.date_recorded).all()

        # Calculate statistics
        if price_history:
            prices = [record.price for record in price_history]
            current_price = product.price or (prices[-1] if prices else 0)
            lowest_price = min(prices) if prices else current_price
            highest_price = max(prices) if prices else current_price
            avg_price = sum(prices) / len(prices) if prices else current_price

            # Calculate best time to buy based on price patterns
            best_time = analyze_best_time_to_buy(price_history)

            # Format for plotting
            history_data = [
                {
                    'date': record.date_recorded.isoformat(),
                    'price': record.price,
                    'is_deal': record.is_deal
                }
                for record in price_history
            ]

            return {
                'product_id': product_id,
                'product_name': product.name,
                'current_price': current_price,
                'lowest_price': lowest_price,
                'highest_price': highest_price,
                'average_price': avg_price,
                'price_history': history_data,
                'best_time_to_buy': best_time,
                'stats_period_days': days
            }
        else:
            return {
                'product_id': product_id,
                'product_name': product.name,
                'current_price': product.price,
                'message': f'No price history available for the last {days} days',
                'price_history': []
            }

    except Exception as e:
        logging.error(f"Error getting price history: {str(e)}")
        return {'error': str(e)}

def create_price_alert(product_id, user_id, target_price=None, percentage_drop=None, notification_method='app'):
    """
    Create a price alert for a specific product

    Args:
        product_id: ID of the product
        user_id: User ID creating the alert
        target_price: Target price that triggers the alert (optional)
        percentage_drop: Percentage drop that triggers the alert (optional)
        notification_method: How to notify the user (default: app)

    Returns:
        Created price alert or error
    """
    try:
        # Ensure either target_price or percentage_drop is provided
        if target_price is None and percentage_drop is None:
            return {'error': 'Either target price or percentage drop is required'}

        # Check if product exists and user has access
        product = Product.query.filter_by(id=product_id, user_id=user_id).first()
        if not product:
            return {'error': 'Product not found or access denied'}

        # Create price alert
        price_alert = PriceAlert(
            product_id=product_id,
            user_id=user_id,
            target_price=target_price,
            percentage_drop=percentage_drop,
            notification_method=notification_method,
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.session.add(price_alert)
        db.session.commit()

        return price_alert

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating price alert: {str(e)}")
        return {'error': str(e)}

def check_price_alerts(product_id, current_price):
    """
    Check if current price triggers any alerts and update them

    Args:
        product_id: ID of the product
        current_price: Current price to check against alerts

    Returns:
        List of triggered alerts
    """
    try:
        # Get all active alerts for this product
        alerts = PriceAlert.query.filter_by(
            product_id=product_id,
            is_active=True
        ).all()

        triggered_alerts = []

        for alert in alerts:
            triggered = False

            # Check if target price alert is triggered
            if alert.target_price and current_price <= alert.target_price:
                triggered = True

            # Check if percentage drop alert is triggered
            if alert.percentage_drop and not triggered:
                # Get previous price from product
                product = Product.query.get(product_id)
                if product:
                    # Calculate the price needed to trigger based on percentage drop
                    highest_price = get_highest_price_since_last_alert(product_id, alert.last_triggered)
                    if highest_price:
                        target = highest_price * (1 - (alert.percentage_drop / 100))
                        if current_price <= target:
                            triggered = True

            # If alert is triggered, update it
            if triggered:
                alert.last_triggered = datetime.utcnow()
                db.session.add(alert)
                triggered_alerts.append(alert)

                # Here you would send notifications based on notification_method
                # This would typically call a notification service

        if triggered_alerts:
            db.session.commit()

        return triggered_alerts

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error checking price alerts: {str(e)}")
        return []

def get_highest_price_since_last_alert(product_id, last_triggered):
    """
    Get the highest price recorded since the last alert was triggered

    Args:
        product_id: ID of the product
        last_triggered: Datetime when the alert was last triggered

    Returns:
        Highest price or None
    """
    try:
        query = PriceHistory.query.filter(
            PriceHistory.product_id == product_id
        )

        if last_triggered:
            query = query.filter(PriceHistory.date_recorded > last_triggered)

        highest_record = query.order_by(PriceHistory.price.desc()).first()

        return highest_record.price if highest_record else None

    except Exception as e:
        logging.error(f"Error getting highest price: {str(e)}")
        return None

def scrape_product_details(url):
    """
    Scrape product details from a URL

    Args:
        url: URL to scrape

    Returns:
        Dictionary with product details
    """
    try:
        source = extract_source_from_url(url)

        if 'amazon' in source.lower():
            return scrape_amazon_product(url)
        elif 'walmart' in source.lower():
            return scrape_walmart_product(url)
        else:
            return scrape_generic_product(url)

    except Exception as e:
        logging.error(f"Error scraping product details: {str(e)}")
        return {'error': str(e)}

def scrape_product_price(url):
    """
    Scrape just the price from a product URL

    Args:
        url: URL to scrape

    Returns:
        Dictionary with price information
    """
    try:
        source = extract_source_from_url(url)

        if 'amazon' in source.lower():
            return scrape_amazon_price(url)
        elif 'walmart' in source.lower():
            return scrape_walmart_price(url)
        else:
            return scrape_generic_price(url)

    except Exception as e:
        logging.error(f"Error scraping product price: {str(e)}")
        return {'error': str(e)}

def extract_source_from_url(url):
    """
    Extract the source (website) from a URL

    Args:
        url: URL to extract source from

    Returns:
        Source name
    """
    try:
        if 'amazon.com' in url:
            return 'Amazon'
        elif 'walmart.com' in url:
            return 'Walmart'
        elif 'target.com' in url:
            return 'Target'
        elif 'bestbuy.com' in url:
            return 'Best Buy'
        elif 'ebay.com' in url:
            return 'eBay'
        else:
            # Extract domain name
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            domain = domain.split('.')[-2] if len(domain.split('.')) > 1 else domain
            return domain.capitalize()

    except Exception:
        return 'Unknown'

def scrape_amazon_product(url):
    """
    Scrape product details from Amazon

    Args:
        url: Amazon product URL

    Returns:
        Dictionary with product details
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code != 200:
            return {'error': f'Failed to fetch page: {response.status_code}'}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product details
        name_elem = soup.select_one('#productTitle')
        name = name_elem.text.strip() if name_elem else None

        # Try different price selectors (Amazon's structure changes often)
        price_elem = soup.select_one('.a-price .a-offscreen')
        if not price_elem:
            price_elem = soup.select_one('#price_inside_buybox')
        if not price_elem:
            price_elem = soup.select_one('#priceblock_ourprice')

        price_text = price_elem.text.strip() if price_elem else None
        price = extract_price(price_text) if price_text else None

        # Extract description
        description_elem = soup.select_one('#productDescription')
        if not description_elem:
            description_elem = soup.select_one('#feature-bullets')
        description = description_elem.text.strip() if description_elem else None

        # Extract image URL
        image_elem = soup.select_one('#landingImage')
        if not image_elem:
            image_elem = soup.select_one('.a-dynamic-image')
        image_url = image_elem.get('src') if image_elem else None

        return {
            'name': name,
            'price': price,
            'description': description,
            'image_url': image_url,
            'source': 'Amazon'
        }

    except Exception as e:
        logging.error(f"Error scraping Amazon product: {str(e)}")
        return {'error': str(e)}

def scrape_amazon_price(url):
    """
    Scrape just the price from an Amazon product URL

    Args:
        url: Amazon product URL

    Returns:
        Dictionary with price information
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code != 200:
            return {'error': f'Failed to fetch page: {response.status_code}'}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try different price selectors
        price_elem = soup.select_one('.a-price .a-offscreen')
        if not price_elem:
            price_elem = soup.select_one('#price_inside_buybox')
        if not price_elem:
            price_elem = soup.select_one('#priceblock_ourprice')

        price_text = price_elem.text.strip() if price_elem else None
        price = extract_price(price_text) if price_text else None

        if not price:
            return {'error': 'Price not found'}

        return {
            'price': price,
            'source': 'Amazon'
        }

    except Exception as e:
        logging.error(f"Error scraping Amazon price: {str(e)}")
        return {'error': str(e)}

def scrape_walmart_product(url):
    """
    Scrape product details from Walmart

    Args:
        url: Walmart product URL

    Returns:
        Dictionary with product details
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code != 200:
            return {'error': f'Failed to fetch page: {response.status_code}'}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product details
        name_elem = soup.select_one('h1[itemprop="name"]')
        if not name_elem:
            name_elem = soup.select_one('.prod-ProductTitle')
        name = name_elem.text.strip() if name_elem else None

        # Try different price selectors
        price_elem = soup.select_one('[data-automation="product-price"]')
        if not price_elem:
            price_elem = soup.select_one('.price-characteristic')

        price_text = price_elem.text.strip() if price_elem else None
        price = extract_price(price_text) if price_text else None

        # Extract description
        description_elem = soup.select_one('.product-description-container')
        description = description_elem.text.strip() if description_elem else None

        # Extract image URL
        image_elem = soup.select_one('.prod-hero-image img')
        image_url = image_elem.get('src') if image_elem else None

        return {
            'name': name,
            'price': price,
            'description': description,
            'image_url': image_url,
            'source': 'Walmart'
        }

    except Exception as e:
        logging.error(f"Error scraping Walmart product: {str(e)}")
        return {'error': str(e)}

def scrape_walmart_price(url):
    """
    Scrape just the price from a Walmart product URL

    Args:
        url: Walmart product URL

    Returns:
        Dictionary with price information
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code != 200:
            return {'error': f'Failed to fetch page: {response.status_code}'}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try different price selectors
        price_elem = soup.select_one('[data-automation="product-price"]')
        if not price_elem:
            price_elem = soup.select_one('.price-characteristic')

        price_text = price_elem.text.strip() if price_elem else None
        price = extract_price(price_text) if price_text else None

        if not price:
            return {'error': 'Price not found'}

        return {
            'price': price,
            'source': 'Walmart'
        }

    except Exception as e:
        logging.error(f"Error scraping Walmart price: {str(e)}")
        return {'error': str(e)}

def scrape_generic_product(url):
    """
    Scrape product details from a generic website

    Args:
        url: Product URL

    Returns:
        Dictionary with product details
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code != 200:
            return {'error': f'Failed to fetch page: {response.status_code}'}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try common selectors for product information
        # Look for name in common places
        name_elem = soup.select_one('h1')
        name = name_elem.text.strip() if name_elem else None

        # Look for price with various common selectors
        price_elem = None
        for selector in ['.price', '[itemprop="price"]', '.product-price', '.current-price']:
            price_elem = soup.select_one(selector)
            if price_elem:
                break

        price_text = price_elem.text.strip() if price_elem else None
        price = extract_price(price_text) if price_text else None

        # Look for description
        description_elem = None
        for selector in ['.description', '[itemprop="description"]', '.product-description']:
            description_elem = soup.select_one(selector)
            if description_elem:
                break

        description = description_elem.text.strip() if description_elem else None

        # Look for image
        image_elem = None
        for selector in ['.product-image img', '[itemprop="image"]', '.main-image img']:
            image_elem = soup.select_one(selector)
            if image_elem:
                break

        image_url = image_elem.get('src') if image_elem else None

        return {
            'name': name,
            'price': price,
            'description': description,
            'image_url': image_url,
            'source': extract_source_from_url(url)
        }

    except Exception as e:
        logging.error(f"Error scraping generic product: {str(e)}")
        return {'error': str(e)}

def scrape_generic_price(url):
    """
    Scrape just the price from a generic product URL

    Args:
        url: Product URL

    Returns:
        Dictionary with price information
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code != 200:
            return {'error': f'Failed to fetch page: {response.status_code}'}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try common selectors for price
        price_elem = None
        for selector in ['.price', '[itemprop="price"]', '.product-price', '.current-price']:
            price_elem = soup.select_one(selector)
            if price_elem:
                break

        price_text = price_elem.text.strip() if price_elem else None
        price = extract_price(price_text) if price_text else None

        if not price:
            return {'error': 'Price not found'}

        return {
            'price': price,
            'source': extract_source_from_url(url)
        }

    except Exception as e:
        logging.error(f"Error scraping generic price: {str(e)}")
        return {'error': str(e)}

def extract_price(price_text):
    """
    Extract price from a price text string

    Args:
        price_text: Text string containing price

    Returns:
        Float price or None
    """
    if not price_text:
        return None

    try:
        # Remove currency symbols and other chars, keep dots and numbers
        cleaned = re.sub(r'[^\d.]', '', price_text.strip())
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def is_likely_deal(product, current_price):
    """
    Check if current price likely represents a deal

    Args:
        product: Product object
        current_price: Current price

    Returns:
        Boolean indicating if it's likely a deal
    """
    try:
        if not product or not current_price:
            return False

        # Get recent price history
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        price_history = PriceHistory.query.filter(
            PriceHistory.product_id == product.id,
            PriceHistory.date_recorded >= thirty_days_ago
        ).all()

        if not price_history or len(price_history) < 3:
            # Not enough history to determine if it's a deal
            return False

        # Calculate average price from history
        prices = [record.price for record in price_history]
        avg_price = sum(prices) / len(prices)

        # If current price is at least 10% below average, it's likely a deal
        return current_price <= (avg_price * 0.9)

    except Exception as e:
        logging.error(f"Error checking if price is a deal: {str(e)}")
        return False

def analyze_best_time_to_buy(price_history):
    """
    Analyze price history to determine the best time to buy

    Args:
        price_history: List of PriceHistory objects

    Returns:
        Dictionary with best time recommendations
    """
    try:
        if not price_history or len(price_history) < 7:
            return {
                'message': 'Not enough price history to determine patterns',
                'confidence': 'low'
            }

        # Group prices by day of week to find patterns
        by_day = {i: [] for i in range(7)}  # 0 = Monday, 6 = Sunday

        for record in price_history:
            day_of_week = record.date_recorded.weekday()
            by_day[day_of_week].append(record.price)

        # Calculate average price for each day
        avg_by_day = {}
        for day, prices in by_day.items():
            if prices:
                avg_by_day[day] = sum(prices) / len(prices)

        if not avg_by_day:
            return {
                'message': 'Unable to determine price patterns',
                'confidence': 'low'
            }

        # Find the day with the lowest average price
        best_day = min(avg_by_day.items(), key=lambda x: x[1])
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Check if there's a significant difference
        all_avgs = list(avg_by_day.values())
        overall_avg = sum(all_avgs) / len(all_avgs)

        # If best day is at least 5% better than average
        if best_day[1] <= (overall_avg * 0.95):
            confidence = 'high' if len(price_history) > 20 else 'medium'
            return {
                'best_day': day_names[best_day[0]],
                'avg_price': best_day[1],
                'overall_avg': overall_avg,
                'savings_pct': ((overall_avg - best_day[1]) / overall_avg) * 100,
                'message': f'{day_names[best_day[0]]} tends to have the best prices',
                'confidence': confidence
            }
        else:
            return {
                'message': 'No significant price variations by day of week',
                'confidence': 'medium'
            }

    except Exception as e:
        logging.error(f"Error analyzing best time to buy: {str(e)}")
        return {
            'message': 'Error analyzing price patterns',
            'confidence': 'low',
            'error': str(e)
        }

def find_seasonal_deals(user_id, category=None):
    """
    Find seasonal deals based on current time of year

    Args:
        user_id: User ID to find deals for
        category: Optional category to filter deals

    Returns:
        List of seasonal deals
    """
    try:
        # Determine current season
        month = datetime.utcnow().month
        if month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        elif month in [9, 10, 11]:
            season = 'fall'
        else:
            season = 'winter'

        # Find active deals for this season
        query = Deal.query.filter(
            Deal.is_verified == True,
            Deal.end_date >= datetime.utcnow()
        )

        # Add category filter if provided
        if category:
            # We could join to products and filter by category
            # For demonstration purposes, we'll filter by name/description
            query = query.filter(
                (Deal.name.ilike(f'%{category}%')) |
                (Deal.description.ilike(f'%{category}%'))
            )

        # Get the deals
        deals = query.all()

        # Filter and rank deals to find seasonal ones
        seasonal_deals = []
        seasonal_keywords = {
            'spring': ['spring', 'easter', 'clean', 'garden', 'outdoor'],
            'summer': ['summer', 'beach', 'bbq', 'grill', 'vacation', 'outdoor'],
            'fall': ['fall', 'autumn', 'back to school', 'halloween', 'thanksgiving'],
            'winter': ['winter', 'holiday', 'christmas', 'new year', 'gift']
        }

        current_keywords = seasonal_keywords.get(season, [])

        for deal in deals:
            # Check if deal is seasonal
            text = (deal.name + ' ' + (deal.description or '')).lower()
            score = 0

            for keyword in current_keywords:
                if keyword in text:
                    score += 1

            if score > 0:
                seasonal_deals.append({
                    'deal': deal,
                    'season_relevance': score
                })

        # Sort by relevance and return
        seasonal_deals.sort(key=lambda x: x['season_relevance'], reverse=True)

        return [item['deal'] for item in seasonal_deals]

    except Exception as e:
        logging.error(f"Error finding seasonal deals: {str(e)}")
        return []