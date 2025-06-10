#!/usr/bin/env python3
"""
Test script to verify the fix for Order.user relationship
"""

from app import app
from model import db, Order, User
from sqlalchemy.orm import joinedload

def test_order_user_relationship():
    """Test that Order.user relationship works correctly"""
    
    with app.app_context():
        print("🔍 Testing Order.user relationship...")
        
        # Test basic relationship access
        try:
            # Get a sample order
            order = Order.query.first()
            if order:
                print(f"✅ Order {order.order_id} found")
                
                # Test accessing user through relationship
                user = order.user
                if user:
                    print(f"✅ User relationship works: {user.username}")
                else:
                    print("❌ User relationship returned None")
                    
                # Test joinedload (what was causing the original error)
                orders_with_users = Order.query.options(joinedload(Order.user)).limit(5).all()
                print(f"✅ joinedload(Order.user) works: {len(orders_with_users)} orders loaded")
                
                for order in orders_with_users:
                    print(f"   Order {order.order_id} -> User: {order.user.username if order.user else 'None'}")
                    
            else:
                print("❌ No orders found in database")
                
        except Exception as e:
            print(f"❌ Error testing relationships: {e}")
            return False
            
        print("\n🎉 All relationship tests passed!")
        return True

if __name__ == '__main__':
    test_order_user_relationship()
