from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
from datetime import datetime, timezone, timedelta
from functools import wraps

# Import models
from model import db, User, Book, BookImage, Review, CartItem, Order, OrderItem, app as model_app

app = Flask(__name__)

# Configurations - Using SQLite for testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', "your-super-secret-jwt-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-for-sessions')

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def login_required(f):
    """Decorator for routes that require user to be logged in via session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator for routes that require admin privileges - password-based access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin session is active
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def get_cart_items(user_id=None):
    """Get cart items for user (from session or database)"""
    if user_id:
        # Database cart for logged-in users
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        cart_data = []
        for item in cart_items:
            book = Book.query.get(item.book_id)
            if book:
                cart_data.append({
                    'cart_item_id': item.cart_item_id,
                    'id': book.book_id,
                    'title': book.title,
                    'author': book.author,
                    'description': book.description,
                    'price': float(book.price) if book.price else 0.0,
                    'quantity': item.quantity,
                    'image_url': get_main_image_url(book.book_id)
                })
        return cart_data
    else:
        # Session cart for anonymous users
        return session.get('cart', [])

def get_main_image_url(book_id):
    """Get main image URL for a book"""
    main_image = BookImage.query.filter_by(book_id=book_id, is_main=True).first()
    return main_image.image_url if main_image else 'static/images/placeholder.png'

def calculate_cart_totals(cart_items):
    """Calculate cart totals"""
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    delivery_charge = 5.99 if 0 < subtotal < 50 else 0
    total = subtotal + delivery_charge
    return subtotal, delivery_charge, total

# ============================================================================
# API ROUTES (for potential external use or AJAX calls)
# ============================================================================

@app.route('/api/health')
def api_health_check():
    return jsonify(message="API is running")

@app.route('/api/products', methods=['GET'])
def api_get_products():
    query = request.args.get('q', '')
    genre = request.args.get('genre', '')
    min_price_str = request.args.get('min_price')
    max_price_str = request.args.get('max_price')

    books_query = Book.query

    if query:
        books_query = books_query.filter(
            (Book.title.ilike(f"%{query}%")) | (Book.description.ilike(f"%{query}%")) | (Book.author.ilike(f"%{query}%"))
        )
    if genre:
        books_query = books_query.filter(Book.genre.ilike(f"%{genre}%"))
    if min_price_str:
        try:
            min_price = float(min_price_str)
            books_query = books_query.filter(Book.price >= min_price)
        except ValueError:
            return jsonify(error="Invalid min_price format"), 400
    if max_price_str:
        try:
            max_price = float(max_price_str)
            books_query = books_query.filter(Book.price <= max_price)
        except ValueError:
            return jsonify(error="Invalid max_price format"), 400

    books = books_query.all()
    books_data = [
        {
            'id': b.book_id,
            'title': b.title,
            'author': b.author,
            'description': b.description,
            'price': float(b.price) if b.price else 0.0,
            'genre': b.genre,
            'publisher': b.publisher,
            'rating_avg': b.rating_avg,
            'stock': b.stock,
            'image_url': get_main_image_url(b.book_id)
        } for b in books
    ]
    return jsonify(books_data)

@app.route('/api/products/<int:book_id>', methods=['GET'])
def api_get_product_detail(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify(error="Book not found"), 404
    
    # Fetch images
    main_image = BookImage.query.filter_by(book_id=book.book_id, is_main=True).first()
    other_images = BookImage.query.filter_by(book_id=book.book_id, is_main=False).all()
    
    images_data = []
    if main_image: 
        images_data.append({'url': main_image.image_url, 'is_main': True})
    images_data.extend([{'url': img.image_url, 'is_main': False} for img in other_images])

    # Fetch reviews
    reviews = Review.query.filter_by(book_id=book.book_id).all()
    reviews_data = [
        {
            'user': User.query.get(r.user_id).username if User.query.get(r.user_id) else 'Anonymous', 
            'rating': r.rating, 
            'description': r.description, 
            'created_at': r.created_at.isoformat()
        }
        for r in reviews
    ]

    book_data = {
        'id': book.book_id,
        'title': book.title,
        'author': book.author,
        'description': book.description,
        'price': float(book.price) if book.price else 0.0,
        'delivery_date_info': f"Expected delivery: {book.delivery_date} business days" if book.delivery_date else "Delivery info not available",
        'genre': book.genre,
        'publisher': book.publisher,
        'isbn': book.isbn,
        'publication_year': book.publication_year,
        'pages': book.pages,
        'language': book.language,
        'format': book.format,
        'rating_avg': book.rating_avg,
        'stock': book.stock,
        'images': images_data,
        'reviews': reviews_data
    }
    return jsonify(book_data)

@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify(error="Missing email, username, or password"), 400

    if User.query.filter_by(email=data['email']).first() or User.query.filter_by(username=data['username']).first():
        return jsonify(error="User already exists with this email or username"), 409

    new_user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        mobile_number=data.get('mobile_number')
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="User created successfully"), 201

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify(error="Missing email or password"), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify(error="Invalid credentials"), 401

    access_token = create_access_token(identity=user.user_id)
    return jsonify(access_token=access_token, user_id=user.user_id, username=user.username)

@app.route('/api/cart', methods=['GET'])
@jwt_required()
def api_view_cart():
    current_user_id = get_jwt_identity()
    cart_items = get_cart_items(current_user_id)
    subtotal, delivery_charge, total = calculate_cart_totals(cart_items)
    return jsonify(cart_items=cart_items, subtotal=subtotal, delivery_charge=delivery_charge, total=total)

@app.route('/api/cart/add/<int:book_id>', methods=['POST'])
@jwt_required()
def api_add_to_cart(book_id):
    current_user_id = get_jwt_identity()
    book = Book.query.get(book_id)
    if not book:
        return jsonify(error="Book not found"), 404

    data = request.get_json()
    quantity = data.get('quantity', 1)
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify(error="Invalid quantity"), 400

    cart_item = CartItem.query.filter_by(user_id=current_user_id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user_id, book_id=book_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    return jsonify(message="Book added to cart")

# ============================================================================
# WEB ROUTES (Server-side rendered pages)
# ============================================================================

@app.route('/')
def index():
    # Get featured books from database
    books = Book.query.limit(6).all()
    
    # Add image_url attribute to each book object for template use
    for book in books:
        book.image_url = get_main_image_url(book.book_id)
    
    # Get dynamic genres for homepage
    genres = get_existing_genres()
    
    return render_template('index.html', books=books, genres=genres)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    genre = request.args.get('genre', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Filter books based on search criteria
    books_query = Book.query
    
    if query:
        books_query = books_query.filter(
            (Book.title.ilike(f"%{query}%")) | (Book.description.ilike(f"%{query}%")) | (Book.author.ilike(f"%{query}%"))
        )
    if genre:
        books_query = books_query.filter(Book.genre.ilike(f"%{genre}%"))
    if min_price is not None:
        books_query = books_query.filter(Book.price >= min_price)
    if max_price is not None:
        books_query = books_query.filter(Book.price <= max_price)
    
    books = books_query.all()
    
    # Add image_url attribute to each book object for template use
    for book in books:
        book.image_url = get_main_image_url(book.book_id)
    
    # Get existing genres for the filter dropdown
    genres = get_existing_genres()
    
    return render_template('search.html', books=books, query=query, genre=genre, genres=genres)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get(book_id)
    if not book:
        return redirect(url_for('index'))
    
    # Get current user
    current_user = get_current_user()
    
    # Check if current user has already reviewed this book
    user_has_reviewed = False
    if current_user:
        existing_review = Review.query.filter_by(
            user_id=current_user.user_id, 
            book_id=book_id
        ).first()
        user_has_reviewed = existing_review is not None
    
    # Get book images
    images = BookImage.query.filter_by(book_id=book_id).all()
    
    # Get reviews
    reviews = Review.query.filter_by(book_id=book_id).all()
    reviews_data = []
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_rating = 0
    
    for review in reviews:
        user = User.query.get(review.user_id)
        reviews_data.append({
            'rating': review.rating,
            'comment': review.description,
            'user': user.username if user else 'Anonymous',
            'created_at': review.created_at
        })
        rating_counts[review.rating] += 1
        total_rating += review.rating
    
    # Calculate rating statistics
    total_reviews = len(reviews)
    avg_rating = round(total_rating / total_reviews, 1) if total_reviews > 0 else 0
    
    # Calculate percentages for rating bars
    rating_percentages = {}
    for rating in range(1, 6):
        rating_percentages[rating] = round((rating_counts[rating] / total_reviews) * 100) if total_reviews > 0 else 0
    
    # Add image_url attribute to book object
    book.image_url = get_main_image_url(book.book_id)
    
    rating_data = {
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'rating_percentages': rating_percentages
    }
    
    return render_template('book.html', 
                         book=book, 
                         reviews=reviews_data, 
                         rating_data=rating_data,
                         current_user=current_user,
                         user_has_reviewed=user_has_reviewed)

@app.route('/signup', methods=['GET', 'POST'])
def web_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        mobile_number = request.form.get('mobile_number')
        
        # Validation
        if not username or not email or not password:
            return render_template('signup.html')
        
        if password != confirm_password:
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            return render_template('signup.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            mobile_number=mobile_number
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('web_login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def web_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        if not email or not password:
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return render_template('login.html')
        
        # Log in user
        session['user_id'] = user.user_id
        session['username'] = user.username
          # Transfer session cart to database if user has items in session
        if 'cart' in session and session['cart']:
            for item in session['cart']:
                existing_cart_item = CartItem.query.filter_by(
                    user_id=user.user_id, 
                    book_id=item['id']
                ).first()
                
                if existing_cart_item:
                    existing_cart_item.quantity += item['quantity']
                else:
                    cart_item = CartItem(
                        user_id=user.user_id,
                        book_id=item['id'],
                        quantity=item['quantity']
                    )
                    db.session.add(cart_item)
            
            db.session.commit()
            session.pop('cart', None)  # Clear session cart
        
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def web_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    book = Book.query.get(book_id)
    if not book:
        return redirect(url_for('index'))
    
    # Check stock availability
    if book.stock <= 0:
        return redirect(request.referrer or url_for('index'))
    
    current_user = get_current_user()
    
    if current_user:
        # Add to database cart with stock validation
        cart_item = CartItem.query.filter_by(user_id=current_user.user_id, book_id=book_id).first()
        if cart_item:
            # Check if adding one more would exceed stock
            if cart_item.quantity >= book.stock:
                return redirect(request.referrer or url_for('index'))
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.user_id, book_id=book_id, quantity=1)
            db.session.add(cart_item)
        db.session.commit()
    else:
        # Add to session cart with stock validation
        if 'cart' not in session:
            session['cart'] = []
        
        # Check if book already in cart
        cart_item = next((item for item in session['cart'] if item['id'] == book_id), None)
        if cart_item:
            # Check if adding one more would exceed stock
            if cart_item['quantity'] >= book.stock:
                return redirect(request.referrer or url_for('index'))
            cart_item['quantity'] += 1
        else:
            session['cart'].append({
                'id': book_id,
                'title': book.title,
                'author': book.author,
                'description': book.description,
                'price': float(book.price) if book.price else 0.0,
                'quantity': 1,
                'image_url': get_main_image_url(book_id)
            })
        session.modified = True
    
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    current_user = get_current_user()
    
    if current_user:        # Remove from database cart
        cart_item = CartItem.query.filter_by(cart_item_id=item_id, user_id=current_user.user_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
    else:
        # Remove from session cart (item_id is actually product_id for session)
        if 'cart' in session:
            session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
            session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    current_user = get_current_user()
    cart_items = get_cart_items(current_user.user_id if current_user else None)
    subtotal, delivery_charge, total = calculate_cart_totals(cart_items)
    
    return render_template('cart.html', 
                         cart_items=cart_items, 
                         subtotal=subtotal, 
                         delivery_charge=delivery_charge, 
                         total=total)

@app.route('/shipping', methods=['GET', 'POST'])
@login_required
def shipping():
    current_user = get_current_user()
    cart_items = get_cart_items(current_user.user_id)
    if not cart_items:
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        # Process shipping and payment
        shipping_data = {
            'full_name': request.form.get('full_name'),
            'street_address': request.form.get('street_address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'postal_code': request.form.get('postal_code'),
            'country': request.form.get('country'),
            'payment_method': request.form.get('payment_method')
        }
          # Check stock availability before processing order
        stock_issues = []
        for item in cart_items:
            book = Book.query.get(item['id'])
            if not book:
                stock_issues.append(f"Book '{item['title']}' no longer exists.")
            elif book.stock < item['quantity']:
                stock_issues.append(f"Only {book.stock} units of '{item['title']}' available (you requested {item['quantity']}).")
        
        if stock_issues:
            return redirect(url_for('cart'))
        
        # Process stock reduction for each item
        try:
            for item in cart_items:
                book = Book.query.get(item['id'])
                if book:
                    book.stock -= item['quantity']
                    if book.stock < 0:
                        book.stock = 0  # Prevent negative stock
            
            # Clear cart after successful order and stock update
            CartItem.query.filter_by(user_id=current_user.user_id).delete()
            db.session.commit()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            return redirect(url_for('cart'))
    
    subtotal, delivery_charge, total = calculate_cart_totals(cart_items)
    
    return render_template('shipping.html', 
                         cart_items=cart_items,
                         subtotal=subtotal, 
                         delivery_charge=delivery_charge, 
                         total=total)

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

# ============================================================================
# ADMIN HELPER FUNCTIONS
# ============================================================================

def get_existing_genres():
    """Fetch all unique genres from existing books"""
    try:
        genres = db.session.query(Book.genre).filter(
            Book.genre.isnot(None),
            Book.genre != ''
        ).distinct().order_by(Book.genre).all()
        
        # Convert tuples to list of strings
        genre_list = [genre[0] for genre in genres if genre[0]]
        return genre_list
    except Exception as e:
        print(f"Error fetching genres: {e}")
        return []

# ============================================================================
# ADMIN ROUTES (Password-based admin access)
# ============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with password authentication"""
    if request.method == 'POST':
        password = request.form.get('admin_password')
        
        # Set your admin password here (change this to a secure password)
        ADMIN_PASSWORD = "AdminSecure2025!"  # Secure admin password
        
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for book management - password-based access"""
    current_user = get_current_user()
    
    books = Book.query.all()
    
    # Add image_url attribute to each book object for template use
    for book in books:
        book.image_url = get_main_image_url(book.book_id)
    
    return render_template('admin_dashboard.html', books=books)

@app.route('/admin/summary')
@admin_required
def admin_summary():
    """Admin summary page with books and orders analytics"""
    
    # Book Statistics
    total_books = Book.query.count()
    total_stock = db.session.query(db.func.sum(Book.stock)).scalar() or 0
    
    # Books by genre
    genre_stats = db.session.query(
        Book.genre, 
        db.func.count(Book.book_id).label('count'),
        db.func.sum(Book.stock).label('total_stock')
    ).group_by(Book.genre).all()
    
    # Low stock books (less than 10)
    low_stock_books = Book.query.filter(Book.stock < 10).order_by(Book.stock.asc()).all()
    
    # Order Statistics
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    # Orders by status
    order_status_stats = db.session.query(
        Order.status,
        db.func.count(Order.order_id).label('count'),
        db.func.sum(Order.total_amount).label('total_amount')
    ).group_by(Order.status).all()
    
    # Recent orders (last 20)
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(20).all()
    
    # Top selling books
    top_books = db.session.query(
        Book.title,
        Book.author,
        Book.price,
        db.func.count(OrderItem.order_item_id).label('times_ordered'),
        db.func.sum(OrderItem.quantity).label('total_sold')
    ).join(OrderItem, Book.book_id == OrderItem.book_id)\
     .group_by(Book.book_id)\
     .order_by(db.func.sum(OrderItem.quantity).desc())\
     .limit(10).all()
    
    # Monthly revenue (last 12 months)
    monthly_revenue = db.session.query(
        db.func.strftime('%Y-%m', Order.order_date).label('month'),
        db.func.sum(Order.total_amount).label('revenue'),
        db.func.count(Order.order_id).label('order_count')
    ).filter(Order.status.in_(['completed', 'delivered']))\
     .group_by(db.func.strftime('%Y-%m', Order.order_date))\
     .order_by(db.func.strftime('%Y-%m', Order.order_date).desc())\
     .limit(12).all()
    
    # Customer statistics
    total_customers = User.query.count()
    customers_with_orders = db.session.query(db.func.count(db.func.distinct(Order.user_id))).scalar() or 0
    
    # Top customers
    top_customers = db.session.query(
        User.username,
        User.email,
        db.func.count(Order.order_id).label('total_orders'),
        db.func.sum(Order.total_amount).label('total_spent')
    ).join(Order, User.user_id == Order.user_id)\
     .group_by(User.user_id)\
     .order_by(db.func.sum(Order.total_amount).desc())\
     .limit(10).all()
    
    return render_template('admin_summary.html',
                         # Book stats
                         total_books=total_books,
                         total_stock=total_stock,
                         genre_stats=genre_stats,
                         low_stock_books=low_stock_books,
                         # Order stats
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         order_status_stats=order_status_stats,
                         recent_orders=recent_orders,
                         top_books=top_books,
                         monthly_revenue=monthly_revenue,
                         # Customer stats
                         total_customers=total_customers,
                         customers_with_orders=customers_with_orders,
                         top_customers=top_customers)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """Admin orders management page with filters"""
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    date_filter = request.args.get('date_range', 'all')
    customer_filter = request.args.get('customer', '')
    sort_by = request.args.get('sort', 'date_desc')
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Orders per page
    
    # Start with base query
    query = Order.query
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter(Order.status == status_filter)
    
    # Apply date range filter
    if date_filter != 'all':
        today = datetime.now().date()
        if date_filter == 'today':
            query = query.filter(db.func.date(Order.order_date) == today)
        elif date_filter == 'week':
            week_ago = today - timedelta(days=7)
            query = query.filter(db.func.date(Order.order_date) >= week_ago)
        elif date_filter == 'month':
            month_ago = today - timedelta(days=30)
            query = query.filter(db.func.date(Order.order_date) >= month_ago)
        elif date_filter == 'quarter':
            quarter_ago = today - timedelta(days=90)
            query = query.filter(db.func.date(Order.order_date) >= quarter_ago)
    
    # Apply customer filter
    if customer_filter:
        query = query.join(User).filter(
            User.username.contains(customer_filter) |
            User.email.contains(customer_filter)
        )
    
    # Apply sorting
    if sort_by == 'date_desc':
        query = query.order_by(Order.order_date.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Order.order_date.asc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Order.total_amount.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Order.total_amount.asc())
    elif sort_by == 'status':
        query = query.order_by(Order.status, Order.order_date.desc())
    
    # Paginate results
    orders = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Get filter statistics
    total_orders = Order.query.count()
    filtered_count = query.count()
    
    # Order status counts for filter badges
    status_counts = {}
    all_statuses = db.session.query(
        Order.status,
        db.func.count(Order.order_id).label('count')
    ).group_by(Order.status).all()
    
    for status, count in all_statuses:
        status_counts[status] = count
    
    # Revenue summary for filtered results
    filtered_orders = query.all()
    filtered_revenue = sum(order.total_amount for order in filtered_orders)
    
    return render_template('admin_orders.html',
                         orders=orders,
                         status_filter=status_filter,
                         date_filter=date_filter,
                         customer_filter=customer_filter,
                         sort_by=sort_by,
                         total_orders=total_orders,
                         filtered_count=filtered_count,
                         status_counts=status_counts,
                         filtered_revenue=filtered_revenue)

@app.route('/admin/order/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    """Admin order detail page"""
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    
    # Add book details to order items
    for item in order_items:
        item.book = Book.query.get(item.book_id)
    
    return render_template('admin_order_detail.html',
                         order=order,
                         order_items=order_items)

@app.route('/admin/order/<int:order_id>/update-status', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'completed', 'cancelled']:
        order.status = new_status
        
        # Update delivery date for completed/delivered orders
        if new_status in ['completed', 'delivered'] and not order.delivery_date:
            order.delivery_date = datetime.now()
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'Order status updated to {new_status}'})
    
    return jsonify({'success': False, 'message': 'Invalid status'})

@app.route('/admin/book/add', methods=['GET', 'POST'])
@admin_required
def admin_add_book():
    """Add new book via web interface"""
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        description = request.form.get('description')
        price = request.form.get('price')
        delivery_date = request.form.get('delivery_date')
        genre = request.form.get('genre')
        publisher = request.form.get('publisher')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        pages = request.form.get('pages')
        language = request.form.get('language')
        format_type = request.form.get('format')
        stock = request.form.get('stock')
        image_url = request.form.get('image_url')
        
        # Validation
        if not title or not author or not price:
            genres = get_existing_genres()
            return render_template('admin_add_book.html', genres=genres)
        
        try:
            price = float(price)
            delivery_date = int(delivery_date) if delivery_date else 7
            stock = int(stock) if stock else 0
            publication_year = int(publication_year) if publication_year else None
            pages = int(pages) if pages else None
        except ValueError:
            genres = get_existing_genres()
            return render_template('admin_add_book.html', genres=genres)
        
        # Create book
        book = Book(
            title=title,
            author=author,
            description=description,
            price=price,
            delivery_date=delivery_date,
            genre=genre,
            publisher=publisher,
            isbn=isbn,
            publication_year=publication_year,
            pages=pages,
            language=language or 'English',
            format=format_type or 'Paperback',
            stock=stock
        )
        
        db.session.add(book)
        db.session.flush()
        
        # Add image if provided
        if image_url:
            main_image = BookImage(
                book_id=book.book_id,
                image_url=image_url,
                is_main=True
            )
            db.session.add(main_image)
        
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    # GET request - fetch existing genres
    genres = get_existing_genres()
    return render_template('admin_add_book.html', genres=genres)

@app.route('/admin/book/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_book(book_id):
    """Edit existing book via web interface"""
    book = Book.query.get(book_id)
    if not book:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.description = request.form.get('description')
        book.genre = request.form.get('genre')
        book.publisher = request.form.get('publisher')
        book.isbn = request.form.get('isbn')
        book.language = request.form.get('language')
        book.format = request.form.get('format')
        
        try:
            book.price = float(request.form.get('price'))
            book.delivery_date = int(request.form.get('delivery_date', 7))
            book.stock = int(request.form.get('stock', 0))
            book.publication_year = int(request.form.get('publication_year')) if request.form.get('publication_year') else None
            book.pages = int(request.form.get('pages')) if request.form.get('pages') else None
        except ValueError:
            genres = get_existing_genres()
            return render_template('admin_edit_book.html', book=book, genres=genres)
        
        # Update main image if provided
        image_url = request.form.get('image_url')
        if image_url:
            main_image = BookImage.query.filter_by(book_id=book_id, is_main=True).first()
            if main_image:
                main_image.image_url = image_url
            else:
                new_image = BookImage(
                    book_id=book_id,
                    image_url=image_url,
                    is_main=True
                )
                db.session.add(new_image)
        
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    # Get current main image and genres
    main_image = BookImage.query.filter_by(book_id=book_id, is_main=True).first()
    current_image_url = main_image.image_url if main_image else ''
    genres = get_existing_genres()
    
    return render_template('admin_edit_book.html', book=book, current_image_url=current_image_url, genres=genres)

@app.route('/admin/book/delete/<int:book_id>')
@admin_required
def admin_delete_book(book_id):
    """Delete book via web interface"""
    book = Book.query.get(book_id)
    if not book:
        return redirect(url_for('admin_dashboard'))
    
    book_title = book.title
      # Delete associated images first
    BookImage.query.filter_by(book_id=book_id).delete()
    # Delete book
    db.session.delete(book)
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_current_year():
    """Make current year available to all templates"""
    return {'current_year': datetime.now().year}

@app.context_processor
def inject_current_user():
    """Make current user available to all templates"""
    return {'get_current_user': get_current_user}

@app.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    """Add a review for a book"""
    book = Book.query.get(book_id)
    if not book:
        return redirect(url_for('index'))
    
    current_user = get_current_user()
    
    # Check if user has already reviewed this book
    existing_review = Review.query.filter_by(
        user_id=current_user.user_id, 
        book_id=book_id
    ).first()
    
    if existing_review:
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Get form data
    rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()
    
    # Validation
    if not rating:
        return redirect(url_for('book_detail', book_id=book_id))
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
    except ValueError:
        return redirect(url_for('book_detail', book_id=book_id))
    
    if not comment:
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Create new review
    new_review = Review(
        user_id=current_user.user_id,
        book_id=book_id,
        rating=rating,
        description=comment,
        created_at=datetime.now()
    )
    
    try:
        db.session.add(new_review)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding review: {e}")
    
    return redirect(url_for('book_detail', book_id=book_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Bookstore database tables checked/created.")
    app.run(debug=True, port=5000)
