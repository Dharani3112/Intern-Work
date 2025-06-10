#!/usr/bin/env python3
"""
Generate Orders and Order Items for MySQL Bookstore Database
This script creates fresh order data directly in MySQL, bypassing SQLite completely.
"""

import os
import sys
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import Flask app and models
from app import app
from model import db, User, Book, Order, OrderItem


def generate_orders():
    """Generate realistic orders and order items"""
    
    with app.app_context():
        try:
            # Check current counts
            user_count = User.query.count()
            book_count = Book.query.count()
            order_count = Order.query.count()
            order_item_count = OrderItem.query.count()
            
            print(f"Current Database Status:")
            print(f"  Users: {user_count}")
            print(f"  Books: {book_count}")
            print(f"  Orders: {order_count}")
            print(f"  Order Items: {order_item_count}")
            print()
            
            if user_count == 0 or book_count == 0:
                print("ERROR: No users or books found in database!")
                return False
            
            # Get all users and books
            users = User.query.all()
            books = Book.query.all()
            
            print(f"Generating orders for {len(users)} users from {len(books)} books...")
            
            # Generate 25-40 orders
            num_orders = random.randint(25, 40)
            orders_created = 0
            items_created = 0
            
            for i in range(num_orders):
                # Random user
                user = random.choice(users)
                
                # Random order date within last 6 months
                days_ago = random.randint(1, 180)
                order_date = datetime.now() - timedelta(days=days_ago)
                
                # Create order
                order = Order(
                    user_id=user.id,
                    total_amount=0.0,  # Will calculate after adding items
                    status=random.choice(['pending', 'shipped', 'delivered', 'cancelled']),
                    created_at=order_date
                )
                
                db.session.add(order)
                db.session.flush()  # Get the order ID
                
                # Add 1-5 items to this order
                num_items = random.randint(1, 5)
                order_total = 0.0
                
                # Select random books for this order (no duplicates)
                selected_books = random.sample(books, min(num_items, len(books)))
                
                for book in selected_books:
                    quantity = random.randint(1, 3)
                    price = float(book.price)
                    subtotal = price * quantity
                    order_total += subtotal
                    
                    order_item = OrderItem(
                        order_id=order.id,
                        book_id=book.id,
                        quantity=quantity,
                        price=price
                    )
                    
                    db.session.add(order_item)
                    items_created += 1
                
                # Update order total
                order.total_amount = round(order_total, 2)
                orders_created += 1
                
                # Progress indicator
                if (i + 1) % 5 == 0:
                    print(f"  Created {i + 1}/{num_orders} orders...")
            
            # Commit all changes
            print("\nCommitting changes to MySQL database...")
            db.session.commit()
            
            print(f"\n✅ SUCCESS!")
            print(f"  Orders created: {orders_created}")
            print(f"  Order items created: {items_created}")
            
            # Verify the data
            print("\nVerifying data in MySQL:")
            final_order_count = Order.query.count()
            final_item_count = OrderItem.query.count()
            print(f"  Total orders in database: {final_order_count}")
            print(f"  Total order items in database: {final_item_count}")
            
            # Sample order details
            print("\nSample Orders:")
            sample_orders = Order.query.limit(3).all()
            for order in sample_orders:
                items = OrderItem.query.filter_by(order_id=order.id).all()
                print(f"  Order #{order.id}: User {order.user_id}, ${order.total_amount:.2f}, {len(items)} items, Status: {order.status}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            db.session.rollback()
            return False


def main():
    """Main function"""
    print("=" * 60)
    print("MySQL Bookstore - Order Data Generator")
    print("=" * 60)
    print("This will create fresh order data in MySQL database.")
    print("No SQLite data will be used or migrated.")
    print()
    
    # Confirm MySQL connection
    try:
        with app.app_context():
            # Test database connection
            db.engine.execute("SELECT 1")
            print("✅ MySQL connection successful")
            
            # Show current database URI
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
            if 'mysql' in db_uri.lower():
                print(f"✅ Using MySQL database: {db_uri.split('@')[1] if '@' in db_uri else 'bookstore_db'}")
            else:
                print(f"⚠️  Warning: Database URI doesn't seem to be MySQL: {db_uri}")
                
    except Exception as e:
        print(f"❌ MySQL connection failed: {str(e)}")
        print("Please check your MySQL server and credentials in .env file")
        return False
    
    print()
    
    # Generate orders
    success = generate_orders()
    
    if success:
        print("\n🎉 Order generation completed successfully!")
        print("Your Flask bookstore app now has fresh order data in MySQL.")
    else:
        print("\n😞 Order generation failed. Please check the errors above.")
    
    return success


if __name__ == "__main__":
    main()
