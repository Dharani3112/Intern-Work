#!/usr/bin/env python3
"""
Simple MySQL Orders Creator
Creates basic order data directly in MySQL without user interaction.
"""

import random
import string
from datetime import datetime, timedelta
from model import app, db, User, Book, Order, OrderItem

def create_sample_orders():
    """Create sample orders directly in MySQL"""
    print("Creating sample orders in MySQL...")
    
    with app.app_context():
        try:
            # Get users and books
            users = User.query.all()
            books = Book.query.all()
            
            print(f"Found {len(users)} users and {len(books)} books")
            
            if not users or not books:
                print("Error: Need both users and books to create orders")
                return False
            
            # Create 50 sample orders
            orders_to_create = 50
            statuses = ['completed', 'shipped', 'processing', 'delivered']
            payment_methods = ['credit_card', 'debit_card', 'paypal']
            
            for i in range(orders_to_create):
                # Random date in last 30 days
                days_ago = random.randint(0, 30)
                order_date = datetime.now() - timedelta(days=days_ago)
                
                # Random user and status
                user = random.choice(users)
                status = random.choice(statuses)
                payment_method = random.choice(payment_methods)
                
                # Random books (1-3 books per order)
                num_books = random.randint(1, 3)
                selected_books = random.sample(books, min(num_books, len(books)))
                
                # Calculate totals
                subtotal = 0.0
                order_items_data = []
                
                for book in selected_books:
                    quantity = random.randint(1, 2)
                    price = float(book.price) if book.price else 19.99
                    subtotal += price * quantity
                    
                    order_items_data.append({
                        'book_id': book.book_id,
                        'quantity': quantity,
                        'price_at_time': price
                    })
                
                delivery_charge = 5.99 if subtotal < 50 else 0.0
                total_amount = subtotal + delivery_charge
                
                # Create order
                order = Order(
                    user_id=user.user_id,
                    order_date=order_date,
                    status=status,
                    subtotal=subtotal,
                    delivery_charge=delivery_charge,
                    total_amount=total_amount,
                    shipping_address=f"123 Main St, City, State 12345",
                    payment_method=payment_method,
                    tracking_number=f"TRK{''.join(random.choices(string.digits, k=8))}"
                )
                
                db.session.add(order)
                db.session.flush()  # Get order ID
                
                # Create order items
                for item_data in order_items_data:
                    order_item = OrderItem(
                        order_id=order.order_id,
                        book_id=item_data['book_id'],
                        quantity=item_data['quantity'],
                        price_at_time=item_data['price_at_time']
                    )
                    db.session.add(order_item)
                
                if (i + 1) % 10 == 0:
                    print(f"Created {i + 1} orders...")
            
            db.session.commit()
            
            # Verify
            final_orders = Order.query.count()
            final_items = OrderItem.query.count()
            
            print(f"Success! Created {final_orders} orders and {final_items} order items")
            return True
            
        except Exception as e:
            print(f"Error creating orders: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("🛒 Simple MySQL Orders Creator")
    print("=" * 40)
    
    success = create_sample_orders()
    
    if success:
        print("✅ Orders created successfully in MySQL!")
        print("✅ Your bookstore now has order data!")
        print("✅ You can test the admin dashboard and user orders")
    else:
        print("❌ Failed to create orders")
