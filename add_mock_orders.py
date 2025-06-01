from app import app
from model import db, User, Book, Order, OrderItem
from datetime import datetime, timedelta
import random
import string

def generate_tracking_number():
    """Generate realistic tracking number"""
    prefix = random.choice(['TRK', 'FDX', 'UPS', 'DHL', 'USPS'])
    suffix = ''.join(random.choices(string.digits, k=10))
    return f"{prefix}{suffix}"

def generate_address():
    """Generate realistic shipping addresses"""
    streets = [
        "123 Main Street", "456 Oak Avenue", "789 Pine Road", "321 Elm Street",
        "654 Maple Drive", "987 Cedar Lane", "147 Birch Court", "258 Willow Way",
        "369 Spruce Street", "741 Aspen Circle", "852 Cherry Lane", "963 Walnut Drive",
        "159 Hickory Road", "357 Poplar Avenue", "753 Sycamore Street", "951 Magnolia Drive"
    ]
    
    cities = [
        ("New York", "NY", "10001"), ("Los Angeles", "CA", "90210"), ("Chicago", "IL", "60601"),
        ("Houston", "TX", "77001"), ("Phoenix", "AZ", "85001"), ("Philadelphia", "PA", "19101"),
        ("San Antonio", "TX", "78201"), ("San Diego", "CA", "92101"), ("Dallas", "TX", "75201"),
        ("San Jose", "CA", "95101"), ("Austin", "TX", "73301"), ("Jacksonville", "FL", "32099"),
        ("Fort Worth", "TX", "76101"), ("Columbus", "OH", "43085"), ("Charlotte", "NC", "28201"),
        ("San Francisco", "CA", "94102"), ("Indianapolis", "IN", "46201"), ("Seattle", "WA", "98101"),
        ("Denver", "CO", "80014"), ("Washington", "DC", "20001")
    ]
    
    street = random.choice(streets)
    city, state, zip_code = random.choice(cities)
    
    return f"{street}, {city}, {state} {zip_code}, USA"

def add_mock_orders():
    with app.app_context():
        print("Starting to add mock order history data...")
        
        # Get all users and books
        users = User.query.all()
        books = Book.query.all()
        
        if not users:
            print("No users found! Please add users first.")
            return
        
        if not books:
            print("No books found! Please add books first.")
            return
        
        print(f"Found {len(users)} users and {len(books)} books")
        
        # Order statuses with realistic distribution
        order_statuses = [
            ('completed', 70),     # 70% completed orders
            ('delivered', 15),     # 15% delivered orders
            ('shipped', 8),        # 8% shipped orders
            ('processing', 4),     # 4% processing orders
            ('cancelled', 2),      # 2% cancelled orders
            ('pending', 1)         # 1% pending orders
        ]
        
        # Payment methods distribution
        payment_methods = [
            ('credit_card', 50),
            ('debit_card', 25),
            ('paypal', 15),
            ('cash_on_delivery', 10)
        ]
        
        orders_added = 0
        order_items_added = 0
        
        # Generate orders for the past 2 years
        start_date = datetime.now() - timedelta(days=730)  # 2 years ago
        end_date = datetime.now()
        
        # Target: Add around 2000-5000 orders
        target_orders = random.randint(2000, 5000)
        
        try:
            for i in range(target_orders):
                # Random order date within the past 2 years
                random_days = random.randint(0, 730)
                order_date = start_date + timedelta(days=random_days)
                
                # Choose random user
                user = random.choice(users)
                
                # Choose order status based on distribution
                status_choices = []
                for status, weight in order_statuses:
                    status_choices.extend([status] * weight)
                order_status = random.choice(status_choices)
                
                # Choose payment method based on distribution
                payment_choices = []
                for method, weight in payment_methods:
                    payment_choices.extend([method] * weight)
                payment_method = random.choice(payment_choices)
                
                # Generate shipping address
                shipping_address = generate_address()
                
                # Generate tracking number for shipped/delivered/completed orders
                tracking_number = None
                if order_status in ['shipped', 'delivered', 'completed']:
                    tracking_number = generate_tracking_number()
                
                # Calculate order totals (will be updated after adding items)
                subtotal = 0.0
                
                # Create order
                order = Order(
                    user_id=user.user_id,
                    order_date=order_date,
                    status=order_status,
                    subtotal=0.0,  # Will be calculated
                    delivery_charge=0.0,  # Will be calculated
                    total_amount=0.0,  # Will be calculated
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                    tracking_number=tracking_number
                )
                
                db.session.add(order)
                db.session.flush()  # Get order_id
                
                # Add 1-8 random books to this order
                num_items = random.randint(1, 8)
                selected_books = random.sample(books, min(num_items, len(books)))
                
                order_subtotal = 0.0
                
                for book in selected_books:
                    quantity = random.randint(1, 3)  # 1-3 copies of each book
                    price_at_time = float(book.price)
                    
                    # Add some price variation (books might have been cheaper/expensive in the past)
                    price_variation = random.uniform(0.8, 1.2)  # ±20% price variation
                    price_at_time *= price_variation
                    price_at_time = round(price_at_time, 2)
                    
                    order_item = OrderItem(
                        order_id=order.order_id,
                        book_id=book.book_id,
                        quantity=quantity,
                        price_at_time=price_at_time
                    )
                    
                    db.session.add(order_item)
                    order_subtotal += price_at_time * quantity
                    order_items_added += 1
                
                # Calculate delivery charge (free shipping over $50)
                delivery_charge = 5.99 if order_subtotal < 50 else 0.0
                total_amount = order_subtotal + delivery_charge
                
                # Update order with calculated totals
                order.subtotal = round(order_subtotal, 2)
                order.delivery_charge = delivery_charge
                order.total_amount = round(total_amount, 2)
                
                orders_added += 1
                
                # Commit every 100 orders to avoid memory issues
                if orders_added % 100 == 0:
                    db.session.commit()
                    print(f"Added {orders_added} orders so far...")
            
            # Final commit
            db.session.commit()
            
            print(f"\n✅ Successfully added {orders_added} orders with {order_items_added} order items!")
            print(f"📊 Order Statistics:")
            
            # Show statistics
            for status, _ in order_statuses:
                count = Order.query.filter_by(status=status).count()
                percentage = (count / orders_added * 100) if orders_added > 0 else 0
                print(f"  - {status.title()}: {count} orders ({percentage:.1f}%)")
            
            print(f"\n💰 Revenue Statistics:")
            total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
                Order.status.in_(['completed', 'delivered'])
            ).scalar() or 0
            print(f"  - Total Revenue (Completed + Delivered): ${total_revenue:,.2f}")
            
            avg_order_value = db.session.query(db.func.avg(Order.total_amount)).scalar() or 0
            print(f"  - Average Order Value: ${avg_order_value:.2f}")
            
            print(f"\n📦 Popular Books (by order frequency):")
            popular_books = db.session.query(
                Book.title,
                Book.author,
                db.func.count(OrderItem.book_id).label('order_count')
            ).join(OrderItem).group_by(Book.book_id).order_by(
                db.func.count(OrderItem.book_id).desc()
            ).limit(10).all()
            
            for i, (title, author, count) in enumerate(popular_books, 1):
                print(f"  {i}. '{title}' by {author} - {count} orders")
                
        except Exception as e:
            print(f"❌ Error adding orders: {e}")
            db.session.rollback()

def add_sample_users():
    """Add sample users if none exist"""
    with app.app_context():
        if User.query.count() > 0:
            print("Users already exist, skipping user creation.")
            return
        
        print("Adding sample users...")
        
        sample_users = [
            {
                'username': 'john_reader',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'mobile_number': '+1-555-0101'
            },
            {
                'username': 'book_lover',
                'email': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'mobile_number': '+1-555-0102'
            },
            {
                'username': 'literature_fan',
                'email': 'mike@example.com',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'mobile_number': '+1-555-0103'
            },
            {
                'username': 'novel_enthusiast',
                'email': 'emily@example.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'mobile_number': '+1-555-0104'
            },
            {
                'username': 'story_seeker',
                'email': 'david@example.com',
                'first_name': 'David',
                'last_name': 'Wilson',
                'mobile_number': '+1-555-0105'
            },
            {
                'username': 'page_turner',
                'email': 'lisa@example.com',
                'first_name': 'Lisa',
                'last_name': 'Anderson',
                'mobile_number': '+1-555-0106'
            },
            {
                'username': 'fiction_finder',
                'email': 'robert@example.com',
                'first_name': 'Robert',
                'last_name': 'Taylor',
                'mobile_number': '+1-555-0107'
            },
            {
                'username': 'chapter_chaser',
                'email': 'jennifer@example.com',
                'first_name': 'Jennifer',
                'last_name': 'Martinez',
                'mobile_number': '+1-555-0108'
            },
            {
                'username': 'word_wanderer',
                'email': 'william@example.com',
                'first_name': 'William',
                'last_name': 'Garcia',
                'mobile_number': '+1-555-0109'
            },
            {
                'username': 'text_traveler',
                'email': 'jessica@example.com',
                'first_name': 'Jessica',
                'last_name': 'Rodriguez',
                'mobile_number': '+1-555-0110'
            },
            {
                'username': 'prose_pioneer',
                'email': 'james@example.com',
                'first_name': 'James',
                'last_name': 'Lee',
                'mobile_number': '+1-555-0111'
            },
            {
                'username': 'manuscript_maven',
                'email': 'mary@example.com',
                'first_name': 'Mary',
                'last_name': 'White',
                'mobile_number': '+1-555-0112'
            },
            {
                'username': 'library_lover',
                'email': 'christopher@example.com',
                'first_name': 'Christopher',
                'last_name': 'Harris',
                'mobile_number': '+1-555-0113'
            },
            {
                'username': 'bookmark_buddy',
                'email': 'amanda@example.com',
                'first_name': 'Amanda',
                'last_name': 'Clark',
                'mobile_number': '+1-555-0114'
            },
            {
                'username': 'reading_rebel',
                'email': 'matthew@example.com',
                'first_name': 'Matthew',
                'last_name': 'Lewis',
                'mobile_number': '+1-555-0115'
            }
        ]
        
        try:
            for user_data in sample_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    mobile_number=user_data['mobile_number']
                )
                user.set_password('password123')  # Simple password for testing
                db.session.add(user)
            
            db.session.commit()
            print(f"✅ Added {len(sample_users)} sample users!")
            
        except Exception as e:
            print(f"❌ Error adding users: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🛒 Mock Order History Generator for Bookstore")
    print("=" * 50)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    # Add sample users if needed
    add_sample_users()
    
    # Add mock orders
    add_mock_orders()
    
    print("\n🎉 Mock order history generation completed!")
    print("You can now view order statistics in your bookstore admin panel.")
