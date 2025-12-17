"""
Product Models - E-commerce and Amazon Integration
Models for product tracking, price monitoring, wishlists, and shopping management
"""

from models.database import db
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship


class ProductCategory(db.Model):
    """Product categories for organization"""
    __tablename__ = 'product_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_id = Column(Integer)
    icon = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Self-referential relationship for subcategories
    parent = relationship("ProductCategory", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category")


class Product(db.Model):
    """Main product model for tracking items from various sources"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    brand = Column(String(100))
    model = Column(String(100))
    sku = Column(String(100))
    upc = Column(String(50))
    
    # Amazon specific fields
    amazon_asin = Column(String(20), unique=True, index=True)
    amazon_url = Column(String(500))
    
    # Other marketplace fields
    walmart_id = Column(String(50))
    target_id = Column(String(50))
    ebay_id = Column(String(50))
    
    # Product details
    category_id = Column(Integer)
    current_price = Column(Float)
    original_price = Column(Float)
    currency = Column(String(3), default='USD')
    availability_status = Column(String(50))  # in_stock, out_of_stock, limited
    
    # Images and media
    primary_image_url = Column(String(500))
    image_urls = Column(JSON)  # Array of image URLs
    
    # Ratings and reviews
    average_rating = Column(Float)
    review_count = Column(Integer, default=0)
    
    # Metadata
    specifications = Column(JSON)  # Product specifications as JSON
    features = Column(JSON)  # Key features as JSON array
    dimensions = Column(JSON)  # Width, height, depth, weight
    
    # Tracking
    is_tracked = Column(Boolean, default=False)
    last_checked = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    price_alerts = relationship("PriceAlert", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")


class PriceHistory(db.Model):
    """Track price changes over time"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    source = Column(String(50))  # amazon, walmart, target, etc.
    availability = Column(String(50))
    discount_percentage = Column(Float)
    promotion_details = Column(Text)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    product = relationship("Product", back_populates="price_history")


class Wishlist(db.Model):
    """User wishlists for organizing desired products"""
    __tablename__ = 'wishlists'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    privacy_level = Column(String(20), default='private')  # private, friends, public
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")


class WishlistItem(db.Model):
    """Items within wishlists"""
    __tablename__ = 'wishlist_items'
    
    id = Column(Integer, primary_key=True)
    wishlist_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    notes = Column(Text)
    target_price = Column(Float)  # Price user wants to pay
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product", back_populates="wishlist_items")


class PriceAlert(db.Model):
    """Price alerts for products"""
    __tablename__ = 'price_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    alert_type = Column(String(20), nullable=False)  # price_drop, back_in_stock, target_price
    target_price = Column(Float)
    percentage_drop = Column(Float)
    is_active = Column(Boolean, default=True)
    notification_methods = Column(JSON)  # ['email', 'push', 'sms']
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    product = relationship("Product", back_populates="price_alerts")


class ProductReview(db.Model):
    """User reviews for products"""
    __tablename__ = 'product_reviews'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(255))
    review_text = Column(Text)
    pros = Column(JSON)  # Array of pros
    cons = Column(JSON)  # Array of cons
    verified_purchase = Column(Boolean, default=False)
    helpful_votes = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    product = relationship("Product", back_populates="reviews")


class ShoppingSession(db.Model):
    """Track shopping sessions and cart abandonment"""
    __tablename__ = 'shopping_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    session_id = Column(String(255), unique=True)
    status = Column(String(20), default='active')  # active, completed, abandoned
    total_items = Column(Integer, default=0)
    total_value = Column(Float, default=0.0)
    currency = Column(String(3), default='USD')
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    abandoned_at = Column(DateTime)
    
    # Relationships
    items = relationship("ShoppingSessionItem", back_populates="session")


class ShoppingSessionItem(db.Model):
    """Items in shopping sessions"""
    __tablename__ = 'shopping_session_items'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    price_at_time = Column(Float)
    source_store = Column(String(50))
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    session = relationship("ShoppingSession", back_populates="items")
    product = relationship("Product")


class DealAlert(db.Model):
    """Track deals and special offers"""
    __tablename__ = 'deal_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    product_id = Column(Integer)
    deal_type = Column(String(50))  # lightning_deal, daily_deal, coupon, clearance
    original_price = Column(Float)
    deal_price = Column(Float)
    discount_percentage = Column(Float)
    deal_description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    quantity_available = Column(Integer)
    quantity_claimed = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    source = Column(String(50))
    deal_url = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    product = relationship("Product")


# Helper functions for product management
def create_product_from_amazon(asin: str, product_data: dict) -> Product:
    """Create a product record from Amazon data"""
    try:
        # Check if product already exists
        existing = Product.query.filter_by(amazon_asin=asin).first()
        if existing:
            return existing
        
        # Create new product
        product = Product(
            name=product_data.get('title', ''),
            description=product_data.get('description', ''),
            brand=product_data.get('brand', ''),
            amazon_asin=asin,
            amazon_url=product_data.get('url', ''),
            current_price=product_data.get('price', 0.0),
            currency=product_data.get('currency', 'USD'),
            availability_status=product_data.get('availability', 'unknown'),
            primary_image_url=product_data.get('main_image', ''),
            image_urls=product_data.get('images', []),
            average_rating=product_data.get('rating', 0.0),
            review_count=product_data.get('review_count', 0),
            specifications=product_data.get('specifications', {}),
            features=product_data.get('features', [])
        )
        
        db.session.add(product)
        db.session.commit()
        
        return product
    
    except Exception as e:
        db.session.rollback()
        raise e


def add_price_history(product_id: int, price: float, source: str = 'amazon') -> PriceHistory:
    """Add a price history entry"""
    try:
        price_entry = PriceHistory(
            product_id=product_id,
            price=price,
            source=source
        )
        
        db.session.add(price_entry)
        
        # Update product's current price
        product = Product.query.get(product_id)
        if product:
            product.current_price = price
            product.last_checked = datetime.now(timezone.utc)
        
        db.session.commit()
        return price_entry
    
    except Exception as e:
        db.session.rollback()
        raise e


def create_price_alert(user_id: int, product_id: int, alert_type: str, **kwargs) -> PriceAlert:
    """Create a price alert for a user"""
    try:
        alert = PriceAlert(
            user_id=user_id,
            product_id=product_id,
            alert_type=alert_type,
            target_price=kwargs.get('target_price'),
            percentage_drop=kwargs.get('percentage_drop'),
            notification_methods=kwargs.get('notification_methods', ['email'])
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    except Exception as e:
        db.session.rollback()
        raise e


def add_to_wishlist(user_id: int, product_id: int, wishlist_id: int = None, **kwargs) -> WishlistItem:
    """Add a product to user's wishlist"""
    try:
        # Get or create default wishlist if not specified
        if not wishlist_id:
            wishlist = Wishlist.query.filter_by(user_id=user_id, is_default=True).first()
            if not wishlist:
                wishlist = Wishlist(
                    user_id=user_id,
                    name="My Wishlist",
                    is_default=True
                )
                db.session.add(wishlist)
                db.session.flush()
            wishlist_id = wishlist.id
        
        # Check if item already exists
        existing = WishlistItem.query.filter_by(
            wishlist_id=wishlist_id,
            product_id=product_id
        ).first()
        
        if existing:
            existing.quantity += kwargs.get('quantity', 1)
            db.session.commit()
            return existing
        
        # Create new wishlist item
        item = WishlistItem(
            wishlist_id=wishlist_id,
            product_id=product_id,
            quantity=kwargs.get('quantity', 1),
            priority=kwargs.get('priority', 'medium'),
            notes=kwargs.get('notes', ''),
            target_price=kwargs.get('target_price')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return item
    
    except Exception as e:
        db.session.rollback()
        raise e


def get_price_trends(product_id: int, days: int = 30) -> dict:
    """Get price trends for a product"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        price_history = PriceHistory.query.filter(
            PriceHistory.product_id == product_id,
            PriceHistory.recorded_at >= cutoff_date
        ).order_by(PriceHistory.recorded_at).all()
        
        if not price_history:
            return {'trend': 'no_data', 'prices': [], 'change': 0}
        
        prices = [entry.price for entry in price_history]
        dates = [entry.recorded_at.isoformat() for entry in price_history]
        
        # Calculate trend
        if len(prices) < 2:
            trend = 'stable'
            change = 0
        else:
            start_price = prices[0]
            end_price = prices[-1]
            change = ((end_price - start_price) / start_price) * 100
            
            if change > 5:
                trend = 'increasing'
            elif change < -5:
                trend = 'decreasing'
            else:
                trend = 'stable'
        
        return {
            'trend': trend,
            'change_percentage': round(change, 2),
            'current_price': prices[-1] if prices else 0,
            'highest_price': max(prices) if prices else 0,
            'lowest_price': min(prices) if prices else 0,
            'prices': prices,
            'dates': dates
        }
    
    except Exception as e:
        return {'trend': 'error', 'error': str(e)}


def search_products(query: str, category_id: int = None, price_range: tuple = None, limit: int = 20) -> list:
    """Search products with filters"""
    try:
        query_obj = Product.query
        
        # Text search
        if query:
            query_obj = query_obj.filter(
                db.or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.description.ilike(f'%{query}%'),
                    Product.brand.ilike(f'%{query}%')
                )
            )
        
        # Category filter
        if category_id:
            query_obj = query_obj.filter(Product.category_id == category_id)
        
        # Price range filter
        if price_range:
            min_price, max_price = price_range
            if min_price:
                query_obj = query_obj.filter(Product.current_price >= min_price)
            if max_price:
                query_obj = query_obj.filter(Product.current_price <= max_price)
        
        # Order by relevance (price, rating, review count)
        products = query_obj.order_by(
            Product.average_rating.desc(),
            Product.review_count.desc()
        ).limit(limit).all()
        
        return products
    
    except Exception as e:
        return []


def get_deal_recommendations(user_id: int, limit: int = 10) -> list:
    """Get personalized deal recommendations"""
    try:
        # Get user's wishlist items
        wishlist_products = db.session.query(Product).join(WishlistItem).join(Wishlist).filter(
            Wishlist.user_id == user_id
        ).all()
        
        # Get active deals for wishlist products
        deals = DealAlert.query.filter(
            DealAlert.product_id.in_([p.id for p in wishlist_products]),
            DealAlert.is_active == True,
            DealAlert.end_time > datetime.now(timezone.utc)
        ).order_by(DealAlert.discount_percentage.desc()).limit(limit).all()
        
        return deals
    
    except Exception as e:
        return []


def initialize_product_categories():
    """Initialize default product categories"""
    default_categories = [
        {'name': 'Electronics', 'description': 'Electronic devices and gadgets', 'icon': '📱'},
        {'name': 'Books', 'description': 'Books and reading materials', 'icon': '📚'},
        {'name': 'Home & Garden', 'description': 'Home improvement and gardening', 'icon': '🏠'},
        {'name': 'Health & Beauty', 'description': 'Health and beauty products', 'icon': '💄'},
        {'name': 'Sports & Outdoors', 'description': 'Sports and outdoor equipment', 'icon': '⚽'},
        {'name': 'Toys & Games', 'description': 'Toys and gaming products', 'icon': '🎮'},
        {'name': 'Clothing', 'description': 'Clothing and accessories', 'icon': '👕'},
        {'name': 'Kitchen', 'description': 'Kitchen and dining products', 'icon': '🍳'},
        {'name': 'Automotive', 'description': 'Automotive parts and accessories', 'icon': '🚗'},
        {'name': 'Pet Supplies', 'description': 'Pet care and supplies', 'icon': '🐕'}
    ]
    
    try:
        for cat_data in default_categories:
            existing = ProductCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = ProductCategory(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        return False