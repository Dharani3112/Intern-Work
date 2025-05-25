from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

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
        # In a real app, you would save this data to a database
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Here you would typically hash the password and save to database
        # For this demo, we'll just redirect to the shipping page
        return redirect(url_for('shipping'))
    
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