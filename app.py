from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
from datetime import datetime, timezone, timedelta
from functools import wraps

# Import models
from model import db, User, Product, ProductImage, Review, CartItem, app as model_app

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
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('web_login'))
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
            product = Product.query.get(item.product_id)
            if product:
                cart_data.append({
                    'cart_item_id': item.cart_item_id,
                    'id': product.product_id,
                    'name': product.name,
                    'description': product.description,
                    'price': float(product.price) if product.price else 0.0,
                    'quantity': item.quantity,
                    'image_url': get_main_image_url(product.product_id)
                })
        return cart_data
    else:
        # Session cart for anonymous users
        return session.get('cart', [])

def get_main_image_url(product_id):
    """Get main image URL for a product"""
    main_image = ProductImage.query.filter_by(product_id=product_id, is_main=True).first()
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
    category = request.args.get('category', '')
    min_price_str = request.args.get('min_price')
    max_price_str = request.args.get('max_price')

    products_query = Product.query

    if query:
        products_query = products_query.filter(
            (Product.name.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%"))
        )
    if category:
        products_query = products_query.filter(Product.category.ilike(f"%{category}%"))
    if min_price_str:
        try:
            min_price = float(min_price_str)
            products_query = products_query.filter(Product.price >= min_price)
        except ValueError:
            return jsonify(error="Invalid min_price format"), 400
    if max_price_str:
        try:
            max_price = float(max_price_str)
            products_query = products_query.filter(Product.price <= max_price)
        except ValueError:
            return jsonify(error="Invalid max_price format"), 400

    products = products_query.all()
    products_data = [
        {
            'id': p.product_id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price) if p.price else 0.0,
            'category': p.category,
            'brand': p.brand,
            'rating_avg': p.rating_avg,
            'stock': p.stock,
            'image_url': get_main_image_url(p.product_id)
        } for p in products
    ]
    return jsonify(products_data)

@app.route('/api/products/<int:product_id>', methods=['GET'])
def api_get_product_detail(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify(error="Product not found"), 404
    
    # Fetch images
    main_image = ProductImage.query.filter_by(product_id=product.product_id, is_main=True).first()
    other_images = ProductImage.query.filter_by(product_id=product.product_id, is_main=False).all()
    
    images_data = []
    if main_image: 
        images_data.append({'url': main_image.image_url, 'is_main': True})
    images_data.extend([{'url': img.image_url, 'is_main': False} for img in other_images])

    # Fetch reviews
    reviews = Review.query.filter_by(product_id=product.product_id).all()
    reviews_data = [
        {
            'user': User.query.get(r.user_id).username if User.query.get(r.user_id) else 'Anonymous', 
            'rating': r.rating, 
            'description': r.description, 
            'created_at': r.created_at.isoformat()
        }
        for r in reviews
    ]

    product_data = {
        'id': product.product_id,
        'name': product.name,
        'description': product.description,
        'specifications': product.specifications,
        'price': float(product.price) if product.price else 0.0,
        'delivery_date_info': f"Expected delivery: {product.delivery_date} business days" if product.delivery_date else "Delivery info not available",
        'category': product.category,
        'brand': product.brand,
        'rating_avg': product.rating_avg,
        'stock': product.stock,
        'images': images_data,
        'reviews': reviews_data
    }
    return jsonify(product_data)

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

@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@jwt_required()
def api_add_to_cart(product_id):
    current_user_id = get_jwt_identity()
    product = Product.query.get(product_id)
    if not product:
        return jsonify(error="Product not found"), 404

    data = request.get_json()
    quantity = data.get('quantity', 1)
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify(error="Invalid quantity"), 400

    cart_item = CartItem.query.filter_by(user_id=current_user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    return jsonify(message="Product added to cart")

# ============================================================================
# WEB ROUTES (Server-side rendered pages)
# ============================================================================

@app.route('/')
def index():
    # Get featured products from database
    products = Product.query.limit(6).all()
    products_data = []
    for product in products:
        products_data.append({
            'id': product.product_id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price) if product.price else 0.0,
            'image_url': get_main_image_url(product.product_id)
        })
    
    return render_template('index.html', products=products_data)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Filter products based on search criteria
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(
            (Product.name.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%"))
        )
    if category:
        products_query = products_query.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        products_query = products_query.filter(Product.price >= min_price)
    if max_price is not None:
        products_query = products_query.filter(Product.price <= max_price)
    
    products = products_query.all()
    products_data = []
    for product in products:
        products_data.append({
            'id': product.product_id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price) if product.price else 0.0,
            'image_url': get_main_image_url(product.product_id)
        })
    
    return render_template('search.html', products=products_data, query=query, category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))
    
    # Get product images
    images = ProductImage.query.filter_by(product_id=product_id).all()
    
    # Get reviews
    reviews = Review.query.filter_by(product_id=product_id).all()
    reviews_data = []
    for review in reviews:
        user = User.query.get(review.user_id)
        reviews_data.append({
            'rating': review.rating,
            'comment': review.description,
            'user': user.username if user else 'Anonymous',
            'created_at': review.created_at
        })
    
    product_data = {
        'id': product.product_id,
        'name': product.name,
        'description': product.description,
        'specifications': product.specifications,
        'price': float(product.price) if product.price else 0.0,
        'image_url': get_main_image_url(product.product_id)
    }
    
    return render_template('product.html', product=product_data, reviews=reviews_data)

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
            flash('Username, email, and password are required.', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('User already exists with this email or username.', 'error')
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
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('web_login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def web_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html')
        
        # Log in user
        session['user_id'] = user.user_id
        session['username'] = user.username
        
        # Transfer session cart to database if user has items in session
        if 'cart' in session and session['cart']:
            for item in session['cart']:
                existing_cart_item = CartItem.query.filter_by(
                    user_id=user.user_id, 
                    product_id=item['id']
                ).first()
                
                if existing_cart_item:
                    existing_cart_item.quantity += item['quantity']
                else:
                    cart_item = CartItem(
                        user_id=user.user_id,
                        product_id=item['id'],
                        quantity=item['quantity']
                    )
                    db.session.add(cart_item)
            
            db.session.commit()
            session.pop('cart', None)  # Clear session cart
        
        flash('Login successful!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def web_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))
    
    current_user = get_current_user()
    
    if current_user:
        # Add to database cart
        cart_item = CartItem.query.filter_by(user_id=current_user.user_id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=current_user.user_id, product_id=product_id, quantity=1)
            db.session.add(cart_item)
        db.session.commit()
    else:
        # Add to session cart
        if 'cart' not in session:
            session['cart'] = []
        
        # Check if product already in cart
        cart_item = next((item for item in session['cart'] if item['id'] == product_id), None)
        if cart_item:
            cart_item['quantity'] += 1
        else:
            session['cart'].append({
                'id': product_id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price) if product.price else 0.0,
                'quantity': 1,
                'image_url': get_main_image_url(product_id)
            })
        session.modified = True
    
    flash('Product added to cart!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    current_user = get_current_user()
    
    if current_user:
        # Remove from database cart
        cart_item = CartItem.query.filter_by(cart_item_id=item_id, user_id=current_user.user_id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart.', 'success')
    else:
        # Remove from session cart (item_id is actually product_id for session)
        if 'cart' in session:
            session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
            session.modified = True
            flash('Item removed from cart.', 'success')
    
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
        flash('Your cart is empty.', 'error')
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
        
        # In a real app, you would:
        # 1. Create an Order record
        # 2. Process payment
        # 3. Send confirmation email
        
        # Clear cart after successful order
        CartItem.query.filter_by(user_id=current_user.user_id).delete()
        db.session.commit()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('index'))
    
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
# ADMIN ROUTES (Simple product management)
# ============================================================================

@app.route('/admin')
@login_required
def admin_dashboard():
    """Simple admin dashboard for product management"""
    current_user = get_current_user()
    # For now, any logged-in user can access admin (in production, add role checking)
    
    products = Product.query.all()
    products_data = []
    for product in products:
        products_data.append({
            'id': product.product_id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price) if product.price else 0.0,
            'stock': product.stock,
            'category': product.category,
            'brand': product.brand,
            'image_url': get_main_image_url(product.product_id)
        })
    
    return render_template('admin_dashboard.html', products=products_data)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    """Add new product via web interface"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        specifications = request.form.get('specifications')
        price = request.form.get('price')
        delivery_date = request.form.get('delivery_date')
        category = request.form.get('category')
        brand = request.form.get('brand')
        stock = request.form.get('stock')
        image_url = request.form.get('image_url')
        
        # Validation
        if not name or not price:
            flash('Product name and price are required.', 'error')
            return render_template('admin_add_product.html')
        
        try:
            price = float(price)
            delivery_date = int(delivery_date) if delivery_date else 7
            stock = int(stock) if stock else 0
        except ValueError:
            flash('Invalid price, delivery date, or stock format.', 'error')
            return render_template('admin_add_product.html')
        
        # Create product
        product = Product(
            name=name,
            description=description,
            specifications=specifications,
            price=price,
            delivery_date=delivery_date,
            category=category,
            brand=brand,
            stock=stock
        )
        
        db.session.add(product)
        db.session.flush()
        
        # Add image if provided
        if image_url:
            main_image = ProductImage(
                product_id=product.product_id,
                image_url=image_url,
                is_main=True
            )
            db.session.add(main_image)
        
        db.session.commit()
        flash(f'Product "{name}" added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_add_product.html')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    """Edit existing product via web interface"""
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.specifications = request.form.get('specifications')
        product.category = request.form.get('category')
        product.brand = request.form.get('brand')
        
        try:
            product.price = float(request.form.get('price'))
            product.delivery_date = int(request.form.get('delivery_date', 7))
            product.stock = int(request.form.get('stock', 0))
        except ValueError:
            flash('Invalid price, delivery date, or stock format.', 'error')
            return render_template('admin_edit_product.html', product=product)
        
        # Update main image if provided
        image_url = request.form.get('image_url')
        if image_url:
            main_image = ProductImage.query.filter_by(product_id=product_id, is_main=True).first()
            if main_image:
                main_image.image_url = image_url
            else:
                new_image = ProductImage(
                    product_id=product_id,
                    image_url=image_url,
                    is_main=True
                )
                db.session.add(new_image)
        
        db.session.commit()
        flash(f'Product "{product.name}" updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Get current main image
    main_image = ProductImage.query.filter_by(product_id=product_id, is_main=True).first()
    current_image_url = main_image.image_url if main_image else ''
    
    return render_template('admin_edit_product.html', product=product, current_image_url=current_image_url)

@app.route('/admin/product/delete/<int:product_id>')
@login_required
def admin_delete_product(product_id):
    """Delete product via web interface"""
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    product_name = product.name
    
    # Delete associated images first
    ProductImage.query.filter_by(product_id=product_id).delete()
    # Delete product
    db.session.delete(product)
    db.session.commit()
    
    flash(f'Product "{product_name}" deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("MySQL tables checked/created.")
    app.run(debug=True, port=5000)