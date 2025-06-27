"""
Amazon integration helper
Provides functions for product search and tracking without requiring API credentials
"""

import os
import re
import json
import logging
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from datetime import datetime

# Import the database models
from models import db, Product

# Constants
AMAZON_BASE_URL = "https://www.amazon.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def search_amazon_products(query, max_results=10):
    """
    Search for products on Amazon without using the API.

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of product dictionaries with basic information
    """
    try:
        # Format the search URL
        search_url = f"{AMAZON_BASE_URL}/s?k={quote_plus(query)}"

        # Set up headers to mimic a browser
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Make the request
        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {"error": f"Failed to search Amazon (Status code: {response.status_code})"}

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all product cards
        product_elements = soup.select('div[data-component-type="s-search-result"]')

        results = []
        for element in product_elements[:max_results]:
            try:
                # Get the product details
                title_element = element.select_one('h2 a span')
                title = title_element.text.strip() if title_element else "Unknown Title"

                # Get the link
                link_element = element.select_one('h2 a')
                link = f"{AMAZON_BASE_URL}{link_element['href']}" if link_element and 'href' in link_element.attrs else None

                # Get the image
                img_element = element.select_one('img')
                img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None

                # Get the price
                price_element = element.select_one('.a-price .a-offscreen')
                price_text = price_element.text.strip() if price_element else "Price not available"
                price = extract_price(price_text)

                # Get the rating
                rating_element = element.select_one('.a-icon-star-small .a-icon-alt')
                rating = rating_element.text.strip() if rating_element else "No rating"

                # Get ASIN (Amazon Standard Identification Number)
                asin = element.get('data-asin', '')

                results.append({
                    'title': title,
                    'link': link,
                    'img_url': img_url,
                    'price': price,
                    'price_text': price_text,
                    'rating': rating,
                    'asin': asin,
                    'source': 'Amazon'
                })
            except Exception as e:
                logging.error(f"Error parsing product element: {str(e)}")
                continue

        return results
    except Exception as e:
        logging.error(f"Error searching Amazon: {str(e)}")
        return {"error": f"Error searching Amazon: {str(e)}"}


def extract_price(price_text):
    """Extract numeric price from text like $29.99"""
    if not price_text:
        return None

    # Extract numbers from the string
    match = re.search(r'(\d+\.\d+|\d+)', price_text)
    if match:
        return float(match.group(1))
    return None


def get_product_details(url_or_asin):
    """
    Get detailed information about a specific product

    Args:
        url_or_asin: Product URL or ASIN

    Returns:
        Dictionary with product details
    """
    try:
        # Determine if input is URL or ASIN
        if url_or_asin.startswith('http'):
            url = url_or_asin
        else:
            # It's an ASIN
            url = f"{AMAZON_BASE_URL}/dp/{url_or_asin}"

        # Set up headers to mimic a browser
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        # Make the request
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {"error": f"Failed to get product details (Status code: {response.status_code})"}

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get the product details
        title_element = soup.select_one('#productTitle')
        title = title_element.text.strip() if title_element else "Unknown Title"

        # Get the price
        price_element = soup.select_one('#priceblock_ourprice') or \
                       soup.select_one('.a-price .a-offscreen') or \
                       soup.select_one('#priceblock_dealprice')
        price_text = price_element.text.strip() if price_element else "Price not available"
        price = extract_price(price_text)

        # Get the image
        img_element = soup.select_one('#landingImage') or soup.select_one('#imgBlkFront')
        img_url = img_element['data-old-hires'] if img_element and 'data-old-hires' in img_element.attrs else \
                 img_element['src'] if img_element and 'src' in img_element.attrs else None

        # Get the description
        description_element = soup.select_one('#productDescription')
        description = description_element.text.strip() if description_element else "No description available"

        # Extract ASIN from URL
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        asin = asin_match.group(1) if asin_match else ""

        return {
            'title': title,
            'description': description,
            'price': price,
            'price_text': price_text,
            'img_url': img_url,
            'url': url,
            'asin': asin,
            'source': 'Amazon'
        }
    except Exception as e:
        logging.error(f"Error getting product details: {str(e)}")
        return {"error": f"Error getting product details: {str(e)}"}


def create_amazon_tracking(user_id, product_data, is_recurring=False, frequency_days=30):
    """
    Add a product to track in the database

    Args:
        user_id: User ID to associate with the product
        product_data: Product information (dict)
        is_recurring: Whether this is a recurring purchase
        frequency_days: Frequency in days for recurring purchases

    Returns:
        Newly created Product object
    """
    try:
        # Create a new product
        product = Product(
            name=product_data.get('title', 'Unknown Product'),
            description=product_data.get('description', ''),
            url=product_data.get('url', ''),
            image_url=product_data.get('img_url', ''),
            price=product_data.get('price', 0),
            source='Amazon',
            is_recurring=is_recurring,
            frequency_days=frequency_days if is_recurring else 0,
            user_id=user_id
        )

        # Set next order date if recurring
        if is_recurring and frequency_days > 0:
            from datetime import datetime, timedelta
            product.next_order_date = datetime.utcnow() + timedelta(days=frequency_days)

        # Save to database
        db.session.add(product)
        db.session.commit()

        return product
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating product tracking: {str(e)}")
        return None


def format_amazon_affiliate_url(url, affiliate_tag=None):
    """
    Format an Amazon URL with an affiliate tag

    Args:
        url: Amazon product URL
        affiliate_tag: Optional affiliate tag to use

    Returns:
        Formatted URL with affiliate tag
    """
    # Default tag in case none is provided
    tag = affiliate_tag or os.environ.get('AMAZON_ASSOCIATE_TAG', 'nous-assistant-20')

    # Check if URL already has a tag
    if 'tag=' in url:
        # Replace existing tag
        url = re.sub(r'tag=[^&]+', f'tag={tag}', url)
    else:
        # Add tag to URL
        separator = '&' if '?' in url else '?'
        url = f"{url}{separator}tag={tag}"

    return url