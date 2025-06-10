#!/usr/bin/env python3
"""
Quick Orders Test
"""

import random
from datetime import datetime, timedelta
from model import app, db, User, Book, Order, OrderItem
from decimal import Decimal

print("🚀 Quick Orders Test")

with app.app_context():
    try:
        # Check current status
        users_count = User.query.count()
        books_count = Book.query.count()
        orders_count = Order.query.count()
        
        print(f"Current status:")
        print(f"  Users: {users_count}")
        print(f"  Books: {books_count}")
        print(f"  Orders: {orders_count}")
        
        if users_count > 0 and books_count > 0:
            # Clear and create 5 simple orders
            OrderItem.query.delete()
            Order.query.delete()
            db.session.commit()
            
            users = User.query.all()
            books = Book.query.all()
            
            for i in range(5):
                user = random.choice(users)
                book = random.choice(books)
                
                order = Order(
                    user_id=user.user_id,
                    order_date=datetime.now(),
                    status='completed',
                    subtotal=Decimal('20.00'),
                    delivery_charge=Decimal('5.00'),
                    total_amount=Decimal('25.00'),
                    shipping_address="Test Address",
                    payment_method='credit_card'
                )
                
                db.session.add(order)
                db.session.flush()
                
                order_item = OrderItem(
                    order_id=order.order_id,
                    book_id=book.book_id,
                    quantity=1,
                    price_at_time=Decimal('20.00')
                )
                
                db.session.add(order_item)
            
            db.session.commit()
            
            print(f"✅ Created {Order.query.count()} orders with {OrderItem.query.count()} items")
        else:
            print("❌ Need users and books first")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
