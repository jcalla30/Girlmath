import sqlite3
import os
import json
from datetime import datetime

# Database setup
DB_PATH = "girlmath.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create products table
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        asin TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        current_price REAL,
        peak_price REAL,
        lowest_price REAL,
        price_data TEXT,  -- Stored as JSON string
        category TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # Create search history table
    c.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asin TEXT,
        url TEXT,
        search_term TEXT,
        search_date TEXT,
        user_id INTEGER,
        FOREIGN KEY(asin) REFERENCES products(asin),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    # Create user favorites table
    c.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asin TEXT,
        added_at TEXT,
        notes TEXT,
        user_id INTEGER,
        FOREIGN KEY(asin) REFERENCES products(asin),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        tier TEXT DEFAULT 'free',
        created_at TEXT,
        last_login TEXT
    )
    ''')
    
    # Create coupon codes table
    c.execute('''
    CREATE TABLE IF NOT EXISTS coupon_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        tier TEXT NOT NULL,
        is_used INTEGER DEFAULT 0,
        created_at TEXT
    )
    ''')
    
    # Add default coupon code
    c.execute("SELECT code FROM coupon_codes WHERE code='crystalcallahan'")
    if not c.fetchone():
        now = datetime.now().isoformat()
        c.execute('''
        INSERT INTO coupon_codes (code, tier, created_at)
        VALUES (?, ?, ?)
        ''', ('crystalcallahan', 'platinum', now))
    
    conn.commit()
    conn.close()

def save_product(product_info):
    """Save product information to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Check if product already exists
    c.execute("SELECT asin FROM products WHERE asin=?", (product_info['asin'],))
    existing = c.fetchone()
    
    price_data_json = json.dumps(product_info['price_data'])
    
    if existing:
        # Update existing product
        c.execute('''
        UPDATE products 
        SET title=?, current_price=?, peak_price=?, lowest_price=?, 
            price_data=?, updated_at=?
        WHERE asin=?
        ''', (
            product_info['title'],
            product_info['current_price'],
            product_info['peak_price'],
            product_info['lowest_price'],
            price_data_json,
            now,
            product_info['asin']
        ))
    else:
        # Insert new product
        category = product_info.get('category', 'unknown')
        c.execute('''
        INSERT INTO products 
        (asin, title, current_price, peak_price, lowest_price, price_data, category, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_info['asin'],
            product_info['title'],
            product_info['current_price'],
            product_info['peak_price'],
            product_info['lowest_price'],
            price_data_json,
            category,
            now,
            now
        ))
    
    conn.commit()
    conn.close()
    
    return True

def get_product(asin):
    """Retrieve product information from database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
    SELECT asin, title, current_price, peak_price, lowest_price, price_data, category
    FROM products WHERE asin=?
    ''', (asin,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return None
    
    asin, title, current_price, peak_price, lowest_price, price_data_json, category = result
    price_data = json.loads(price_data_json)
    
    return {
        'asin': asin,
        'title': title,
        'current_price': current_price,
        'peak_price': peak_price,
        'lowest_price': lowest_price,
        'price_data': price_data,
        'category': category,
        'demo': False  # Coming from DB, not generated
    }

def add_search_history(asin=None, url=None, search_term=None):
    """Add entry to search history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    c.execute('''
    INSERT INTO search_history (asin, url, search_term, search_date)
    VALUES (?, ?, ?, ?)
    ''', (asin, url, search_term, now))
    
    conn.commit()
    conn.close()
    
    return True

def get_recent_searches(limit=10):
    """Get recent searches from the database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
    SELECT sh.asin, sh.url, sh.search_term, sh.search_date, p.title, p.current_price
    FROM search_history sh
    LEFT JOIN products p ON sh.asin = p.asin
    ORDER BY sh.search_date DESC
    LIMIT ?
    ''', (limit,))
    
    results = c.fetchall()
    conn.close()
    
    searches = []
    for row in results:
        asin, url, search_term, search_date, title, price = row
        searches.append({
            'asin': asin,
            'url': url,
            'search_term': search_term,
            'search_date': search_date,
            'title': title,
            'current_price': price
        })
    
    return searches

def toggle_favorite(asin, notes=None):
    """Add or remove an item from favorites"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if already in favorites
    c.execute("SELECT id FROM favorites WHERE asin=?", (asin,))
    existing = c.fetchone()
    
    now = datetime.now().isoformat()
    
    if existing:
        # Remove from favorites
        c.execute("DELETE FROM favorites WHERE asin=?", (asin,))
        is_favorite = False
    else:
        # Add to favorites
        c.execute('''
        INSERT INTO favorites (asin, added_at, notes)
        VALUES (?, ?, ?)
        ''', (asin, now, notes))
        is_favorite = True
    
    conn.commit()
    conn.close()
    
    return is_favorite

def get_favorites():
    """Get all favorite products"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
    SELECT f.asin, f.added_at, f.notes, p.title, p.current_price
    FROM favorites f
    JOIN products p ON f.asin = p.asin
    ORDER BY f.added_at DESC
    ''')
    
    results = c.fetchall()
    conn.close()
    
    favorites = []
    for row in results:
        asin, added_at, notes, title, price = row
        favorites.append({
            'asin': asin,
            'added_at': added_at,
            'notes': notes,
            'title': title,
            'current_price': price
        })
    
    return favorites

def is_favorite(asin):
    """Check if a product is in favorites"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT id FROM favorites WHERE asin=?", (asin,))
    result = c.fetchone()
    
    conn.close()
    
    return bool(result)

# User account functions
def create_user(username, password, email=None, tier="free"):
    """Create a new user account"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    try:
        c.execute('''
        INSERT INTO users (username, password, email, tier, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, email, tier, now, now))
        
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        return user_id
    except sqlite3.IntegrityError:
        # Username already exists
        conn.close()
        return None

def check_login(username, password):
    """Verify login credentials and return user info"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
    SELECT id, username, email, tier
    FROM users
    WHERE username=? AND password=?
    ''', (username, password))
    
    result = c.fetchone()
    
    if result:
        # Update last login time
        now = datetime.now().isoformat()
        c.execute('''
        UPDATE users SET last_login=? WHERE id=?
        ''', (now, result[0]))
        conn.commit()
        
        user_info = {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'tier': result[3]
        }
    else:
        user_info = None
    
    conn.close()
    return user_info

def verify_coupon(coupon_code):
    """Verify coupon code and return tier if valid"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
    SELECT tier, is_used
    FROM coupon_codes
    WHERE code=?
    ''', (coupon_code,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return None  # Coupon doesn't exist
    
    tier, is_used = result
    
    if is_used:
        return False  # Coupon already used
    
    return tier

def apply_coupon(coupon_code, user_id):
    """Apply a coupon code to a user account"""
    # Verify coupon first
    tier = verify_coupon(coupon_code)
    
    if not tier or tier is False:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Mark coupon as used
    c.execute('''
    UPDATE coupon_codes SET is_used=1 WHERE code=?
    ''', (coupon_code,))
    
    # Update user tier
    c.execute('''
    UPDATE users SET tier=? WHERE id=?
    ''', (tier, user_id))
    
    conn.commit()
    conn.close()
    
    return tier

def get_user_tier_features(tier):
    """Get features available for a specific tier"""
    tier_features = {
        # Free tier - "Barbie Basic"
        "free": {
            "name": "Barbie Basic",
            "price": "Free",
            "description": "The basic tier for everyday shoppers.",
            "features": [
                "Price history from Amazon",
                "Current prices from different retailers",
                "Basic Girl Math calculations"
            ],
            "max_searches_per_day": 10,
            "access_to_walmart_prices": True,
            "access_to_target_prices": False,
            "purchase_recommendations": False,
            "background": "#FFD1DC"
        },
        # Middle tier - "Clueless Besties"
        "besties": {
            "name": "Clueless Besties",
            "price": "$0.99/month",
            "description": "As if you'd shop without all this data!",
            "features": [
                "Everything in Basic tier",
                "Price history from multiple retailers",
                "Advanced Girl Math calculations",
                "Price alerts via email",
                "Save unlimited favorites"
            ],
            "max_searches_per_day": 50,
            "access_to_walmart_prices": True,
            "access_to_target_prices": True,
            "purchase_recommendations": False,
            "background": "#FFB6C1"
        },
        # Top tier - "Mean Girls Platinum"
        "platinum": {
            "name": "Mean Girls Platinum",
            "price": "$5.00/month",
            "description": "So fetch! The ultimate shopping experience.",
            "features": [
                "Everything in Besties tier",
                "Price predictions and best time to buy",
                "Personalized shopping recommendations",
                "Early access to new features",
                "Custom shopping lists",
                "Priority customer support"
            ],
            "max_searches_per_day": None,  # Unlimited
            "access_to_walmart_prices": True,
            "access_to_target_prices": True,
            "purchase_recommendations": True,
            "background": "#FF69B4"
        }
    }
    
    return tier_features.get(tier, tier_features["free"])

# Initialize the database when the module is imported
init_db()