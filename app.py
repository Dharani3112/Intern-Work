from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Dharani$1@localhost/shopping_site'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    mobile_number = db.Column(db.String(20))

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    specifications = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    delivery_date = db.Column(db.Integer)
    category = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    rating_avg = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)

class ProductImage(db.Model):
    __tablename__ = 'product_images'
    image_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    image_url = db.Column(db.Text)
    is_main = db.Column(db.Boolean, default=False)

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
    )

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)

class Address(db.Model):
    __tablename__ = 'addresses'
    address_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)

# Sample product data (in a real app, this would come from a database)
products = [
    {
        'id': 1,
        'name': 'Wireless Headphones',
        'description': 'Premium quality wireless headphones with noise cancellation and 20-hour battery life.',
        'price': 99.99,
        'image': 'headphones.jpg'
    },
    {
        'id': 2,
        'name': 'Smart Watch',
        'description': 'Advanced fitness tracking, heart rate monitoring, and smartphone notifications.',
        'price': 199.99,
        'image': 'smartwatch.jpg'
    },
    {
        'id': 3,
        'name': 'Laptop Bag',
        'description': 'Durable and stylish laptop bag with multiple compartments and water-resistant material.',
        'price': 49.99,
        'image': 'laptop_bag.jpg'
    },
    {
        'id': 4,
        'name': 'Coffee Maker',
        'description': 'Programmable coffee maker with thermal carafe and auto-brew functionality.',
        'price': 79.99,
        'image': 'coffee_maker.jpg'
    },
    {
        'id': 5,
        'name': 'Yoga Mat',
        'description': 'Non-slip yoga mat with extra cushioning, perfect for home workouts and studio sessions.',
        'price': 29.99,
        'image': 'yoga_mat.jpg'
    }
]

# Create database tables
def create_tables():
    """Create database tables if they don't exist"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Context processor to inject current year into all templates
@app.context_processor
def inject_current_year():
    """Make current year available to all templates"""
    return {'current_year': datetime.now().year}

# Initialize cart in session if it doesn't exist
def init_cart():
    if 'cart' not in session:
        session['cart'] = []

@app.route('/')
def index():
    init_cart()
    return render_template('index.html', products=products)

@app.route('/search')
def search():
    init_cart()
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Filter products based on search criteria
    filtered_products = products
    
    if query:
        filtered_products = [p for p in filtered_products if query.lower() in p['name'].lower() or query.lower() in p['description'].lower()]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p['price'] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p['price'] <= max_price]
    
    return render_template('search.html', products=filtered_products, query=query, category=category)

@app.route('/product/<int:product_id>')
def product(product_id):
    init_cart()
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        return redirect(url_for('index'))
    
    # Sample reviews data
    reviews = [
        {'rating': 5, 'comment': 'Excellent product! Highly recommend.'},
        {'rating': 4, 'comment': 'Good quality, fast shipping.'},
        {'rating': 5, 'comment': 'Perfect! Exactly what I was looking for.'},
        {'rating': 3, 'comment': 'Decent product, could be better.'},
        {'rating': 4, 'comment': 'Good value for money.'}
    ]
    
    return render_template('product.html', product=product, reviews=reviews)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    init_cart()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        # Check if product already in cart
        cart_item = next((item for item in session['cart'] if item['id'] == product_id), None)
        if cart_item:
            cart_item['quantity'] += 1
        else:
            cart_product = product.copy()
            cart_product['quantity'] = 1
            session['cart'].append(cart_product)
        session.modified = True
    
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    init_cart()
    session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    init_cart()
    cart_items = session.get('cart', [])
    
    # Calculate totals
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    delivery_charge = 5.99 if subtotal > 0 and subtotal < 50 else 0
    total = subtotal + delivery_charge
    
    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, delivery_charge=delivery_charge, total=total)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        mobile = request.form.get('mobile')
        date_of_birth = request.form.get('date_of_birth')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different email.', 'error')
            return redirect(url_for('signup'))
        
        # Create username from email (you can modify this logic)
        username = email.split('@')[0]
        
        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            username = f"{username}_{User.query.count() + 1}"
        
        try:
            # Hash password and create new user
            password_hash = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile
            )
            
            # Save to database
            db.session.add(new_user)
            db.session.commit()
            
            # Log in the user
            session['user_id'] = new_user.user_id
            flash('Account created successfully!', 'success')
            
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        # Check if user exists and password is correct
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('login'))
            
        # Log in user and create session
        session['user_id'] = user.user_id
        
        # If user was trying to access a specific page, redirect there
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')
            
        flash('Login successful!', 'success')
        return redirect(next_page)
        
    return render_template('login.html')

@app.route('/forgot-password')
def forgot_password():
    # Placeholder for password reset functionality
    return "Password reset functionality will be implemented here"


@app.route('/shipping', methods=['GET', 'POST'])
def shipping():
    init_cart()
    cart_items = session.get('cart', [])
    
    if not cart_items:
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        # In a real app, you would process the order here
        shipping_data = {
            'full_name': request.form.get('full_name'),
            'street_address': request.form.get('street_address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'postal_code': request.form.get('postal_code'),
            'country': request.form.get('country'),
            'card_name': request.form.get('card_name'),
            'card_number': request.form.get('card_number'),
            'expiry_date': request.form.get('expiry_date'),
            'cvv': request.form.get('cvv')
        }
        
        # Clear cart after successful order
        session['cart'] = []
        session.modified = True
        
        # In a real app, you would redirect to an order confirmation page
        return redirect(url_for('index'))
    
    # Calculate totals for display
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    delivery_charge = 5.99 if subtotal < 50 else 0
    total = subtotal + delivery_charge
    
    return render_template('shipping.html', subtotal=subtotal, delivery_charge=delivery_charge, total=total)

if __name__ == '__main__':
    app.run(debug=True)