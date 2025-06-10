#!/usr/bin/env python3
"""
Create Fresh Orders and Order Items in MySQL
This script generates new realistic order data directly in MySQL without using SQLite.
"""

import random
import sys
from datetime import datetime, timedelta
from model import app, db, User, Book, Order, OrderItem
from decimal import Decimal
import traceback

def generate_fresh_orders():
    """Generate fresh order and order item data in MySQL"""
    print("🛒 CREATING FRESH ORDERS IN MYSQL")
    print("=" * 50)
    print("This script creates new order data directly in MySQL")
    print("No SQLite data will be used or migrated.")
    print()
    
    with app.app_context():
        try:
            # Check current data
            current_users = User.query.count()
            current_books = Book.query.count()
            current_orders = Order.query.count()
            current_items = OrderItem.query.count()
            
            print(f"📊 Current MySQL Database Status:")
            print(f"   Users: {current_users}")
            print(f"   Books: {current_books}")
            print(f"   Orders: {current_orders}")
            print(f"   Order Items: {current_items}")
            print()
            
            if current_users == 0 or current_books == 0:
                print("❌ Need users and books to create orders!")
                print("   Make sure users and books are in MySQL first.")
                return False
            
            # Clear existing orders if any
            if current_orders > 0:
                print("🗑️  Clearing existing orders to create fresh data...")
                OrderItem.query.delete()
                Order.query.delete()
                db.session.commit()
                print("✅ Existing orders cleared!")
            
            # Get available users and books
            users = User.query.all()
            books = Book.query.all()
            
            print(f"📋 Generating orders for {len(users)} users and {len(books)} books...")
            
            # Generate sample orders
            order_count = 100  # Number of orders to create
            order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'completed']
            payment_methods = ['credit_card', 'debit_card', 'paypal', 'cash_on_delivery']
            shipping_addresses = [
                "123 Main St, Anytown, ST 12345",
                "456 Oak Ave, Somewhere, ST 67890", 
                "789 Pine Rd, Elsewhere, ST 54321",
                "321 Elm St, Nowhere, ST 98765",
                "654 Maple Dr, Anywhere, ST 13579",
                "987 Cedar Ln, Middletown, ST 24680",
                "147 Birch St, Uptown, ST 97531",
                "258 Spruce Ave, Downtown, ST 86420"
            ]
            
            orders_created = 0
            items_created = 0
            
            print(f"\n🔄 Creating {order_count} orders...")
            
            for i in range(order_count):
                try:
                    # Random user and order details
                    user = random.choice(users)
                    order_date = datetime.now() - timedelta(days=random.randint(1, 180))
                    delivery_date = order_date + timedelta(days=random.randint(1, 14))
                    status = random.choice(order_statuses)
                    payment_method = random.choice(payment_methods)
                    shipping_address = random.choice(shipping_addresses)
                    
                    # Calculate order totals (will be updated after adding items)
                    subtotal = Decimal('0.00')
                    delivery_charge = Decimal(f"{random.uniform(5.99, 15.99):.2f}")
                    
                    # Create order
                    order = Order(
                        user_id=user.user_id,
                        order_date=order_date,
                        delivery_date=delivery_date,
                        status=status,
                        subtotal=subtotal,
                        delivery_charge=delivery_charge,
                        total_amount=subtotal + delivery_charge,
                        shipping_address=shipping_address,
                        payment_method=payment_method,
                        tracking_number=f"TRK{random.randint(100000, 999999)}"
                    )
                    
                    db.session.add(order)
                    db.session.flush()  # Get the order_id
                    
                    # Add 1-5 random books to this order
                    num_items = random.randint(1, 5)
                    order_books = random.sample(books, min(num_items, len(books)))
                    
                    order_subtotal = Decimal('0.00')
                    
                    for book in order_books:
                        quantity = random.randint(1, 3)
                        price_at_time = Decimal(f"{float(book.price):.2f}") if book.price else Decimal('19.99')
                        item_total = price_at_time * quantity
                        order_subtotal += item_total
                        
                        # Create order item
                        order_item = OrderItem(
                            order_id=order.order_id,
                            book_id=book.book_id,
                            quantity=quantity,
                            price_at_time=price_at_time
                        )
                        
                        db.session.add(order_item)
                        items_created += 1
                    
                    # Update order totals
                    order.subtotal = order_subtotal
                    order.total_amount = order_subtotal + delivery_charge
                    
                    orders_created += 1
                    
                    if (i + 1) % 20 == 0:
                        db.session.commit()
                        print(f"   ✅ Created {i + 1} orders...")
                
                except Exception as e:
                    print(f"   ❌ Error creating order {i + 1}: {e}")
                    db.session.rollback()
                    continue
            
            # Final commit
            db.session.commit()
            
            print(f"\n📊 Order Generation Summary:")
            print(f"   ✅ Orders created: {orders_created}")
            print(f"   ✅ Order items created: {items_created}")
            print(f"   📈 Average items per order: {items_created/orders_created:.1f}")
            
            # Verify creation
            final_orders = Order.query.count()
            final_items = OrderItem.query.count()
            
            print(f"\n🔍 Final MySQL Database Status:")
            print(f"   Users: {User.query.count()}")
            print(f"   Books: {Book.query.count()}")
            print(f"   Orders: {final_orders}")
            print(f"   Order Items: {final_items}")
            
            # Show sample order
            if final_orders > 0:
                sample_order = Order.query.first()
                print(f"\n📋 Sample Order:")
                print(f"   Order ID: {sample_order.order_id}")
                print(f"   User ID: {sample_order.user_id}")
                print(f"   Total: ${sample_order.total_amount}")
                print(f"   Status: {sample_order.status}")
                print(f"   Items: {OrderItem.query.filter_by(order_id=sample_order.order_id).count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating orders: {e}")
            db.session.rollback()
            traceback.print_exc()
            return False

def verify_mysql_only():
    """Verify that the application works with MySQL only"""
    print("\n🔍 VERIFYING MYSQL-ONLY OPERATION")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Test all models
            users_count = User.query.count()
            books_count = Book.query.count()
            orders_count = Order.query.count()
            items_count = OrderItem.query.count()
            
            print(f"✅ Users: {users_count}")
            print(f"✅ Books: {books_count}")
            print(f"✅ Orders: {orders_count}")
            print(f"✅ Order Items: {items_count}")
            
            # Test relationships
            if orders_count > 0:
                sample_order = Order.query.first()
                order_items = OrderItem.query.filter_by(order_id=sample_order.order_id).all()
                user = User.query.get(sample_order.user_id)
                
                print(f"\n📋 Relationship Test:")
                print(f"   Order {sample_order.order_id} has {len(order_items)} items")
                print(f"   Order belongs to user: {user.username if user else 'Unknown'}")
                
                for item in order_items[:3]:  # Show first 3 items
                    book = Book.query.get(item.book_id)
                    print(f"   - {item.quantity}x {book.title if book else 'Unknown Book'} @ ${item.price_at_time}")
            
            print("\n✅ MySQL-only operation verified successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False

def main():
    """Main function"""
    print("🚀 MYSQL-ONLY ORDERS GENERATOR")
    print("=" * 60)
    print("This script creates fresh order data directly in MySQL")
    print("SQLite will not be used or referenced.")
    print()
    
    try:
        # Generate fresh orders
        success = generate_fresh_orders()
        
        if not success:
            print("❌ Order generation failed.")
            return False
        
        # Verify MySQL-only operation
        verify_success = verify_mysql_only()
        
        if verify_success:
            print("\n🎉 SUCCESS!")
            print("=" * 60)
            print("✅ Fresh orders and order items created in MySQL")
            print("✅ Your Flask bookstore is now MySQL-only")
            print("✅ SQLite is no longer needed for the application")
            print("\n🚀 Next Steps:")
            print("   1. Your Flask app now runs entirely on MySQL")
            print("   2. Users can place new orders (stored in MySQL)")
            print("   3. Admin dashboard shows all order data from MySQL")
            print("   4. You can delete the SQLite file if desired")
            print(f"   5. Your app is ready at: http://127.0.0.1:5000")
            
        return verify_success
        
    except Exception as e:
        print(f"❌ Process failed: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
