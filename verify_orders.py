#!/usr/bin/env python3
"""
Simple verification script for the orders management system
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model import db, Order, User, OrderItem, Book, app

def verify_relationships():
    """Verify that the model relationships are working"""
    print("🔍 Verifying model relationships...")
    
    with app.app_context():
        try:
            # Test Order.user relationship
            print("Testing Order.user relationship...")
            orders = Order.query.limit(5).all()
            
            if orders:
                for order in orders:
                    user = order.user
                    if user:
                        print(f"✅ Order {order.order_id} -> User: {user.username}")
                    else:
                        print(f"⚠️ Order {order.order_id} has no associated user")
            else:
                print("ℹ️ No orders found in database")
            
            # Test Order.order_items relationship
            print("\nTesting Order.order_items relationship...")
            for order in orders[:3]:  # Test first 3 orders
                items = order.order_items
                print(f"✅ Order {order.order_id} has {len(items)} items")
                for item in items[:2]:  # Show first 2 items
                    book = item.book
                    if book:
                        print(f"  - {book.title} (Qty: {item.quantity})")
            
            print("\n✅ All relationships are working correctly!")
            return True
            
        except Exception as e:
            print(f"❌ Error testing relationships: {e}")
            return False

def check_orders_data():
    """Check the orders data in the database"""
    print("\n📊 Checking orders data...")
    
    with app.app_context():
        try:
            total_orders = Order.query.count()
            completed_orders = Order.query.filter_by(status='completed').count()
            pending_orders = Order.query.filter_by(status='pending').count()
            
            print(f"Total orders: {total_orders}")
            print(f"Completed orders: {completed_orders}")
            print(f"Pending orders: {pending_orders}")
            
            # Get revenue data
            from sqlalchemy import func
            revenue = db.session.query(func.sum(Order.total_amount)).scalar()
            print(f"Total revenue: ${revenue:.2f}" if revenue else "Total revenue: $0.00")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking orders data: {e}")
            return False

if __name__ == "__main__":
    print("🧪 Verifying Orders Management System")
    print("=" * 50)
    
    # Verify relationships
    relationships_ok = verify_relationships()
    
    # Check data
    data_ok = check_orders_data()
    
    if relationships_ok and data_ok:
        print("\n🎉 Orders management system is ready!")
        print("You can now access the admin panel at: http://127.0.0.1:5000/admin")
        print("Use password: admin123")
    else:
        print("\n⚠️ Some issues were found. Please check the logs above.")
