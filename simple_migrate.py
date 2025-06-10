#!/usr/bin/env python3
"""
Simple Data Migration Script
Transfers data from SQLite to MySQL after tables are created.
"""

import sqlite3
import os
from model import app, db, User, Book, BookImage, Review, CartItem, Order, OrderItem
from datetime import datetime

def migrate_data():
    """Migrate data from SQLite to MySQL"""
    
    print("🔄 Starting data migration...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    sqlite_conn.row_factory = sqlite3.Row  # This allows column access by name
    
    with app.app_context():
        try:
            # Migrate Users
            print("👥 Migrating users...")
            cursor = sqlite_conn.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            for user_row in users:
                # Check if user already exists
                existing_user = User.query.filter_by(user_id=user_row['user_id']).first()
                if not existing_user:
                    user = User(
                        user_id=user_row['user_id'],
                        username=user_row['username'],
                        email=user_row['email'],
                        password_hash=user_row['password_hash'],
                        first_name=user_row.get('first_name'),
                        last_name=user_row.get('last_name'),
                        mobile_number=user_row.get('mobile_number')
                    )
                    db.session.add(user)
            
            db.session.commit()
            print(f"✅ Migrated {len(users)} users")
            
            # Migrate Books
            print("📚 Migrating books...")
            cursor = sqlite_conn.execute("SELECT * FROM books")
            books = cursor.fetchall()
            
            for book_row in books:
                existing_book = Book.query.filter_by(book_id=book_row['book_id']).first()
                if not existing_book:
                    book = Book(
                        book_id=book_row['book_id'],
                        title=book_row['title'],
                        author=book_row['author'],
                        isbn=book_row.get('isbn'),
                        publisher=book_row.get('publisher'),
                        publication_year=book_row.get('publication_year'),
                        pages=book_row.get('pages'),
                        language=book_row.get('language', 'English'),
                        description=book_row.get('description'),
                        price=book_row.get('price'),
                        delivery_date=book_row.get('delivery_date'),
                        genre=book_row.get('genre'),
                        format=book_row.get('format', 'Paperback'),
                        rating_avg=book_row.get('rating_avg', 0.0),
                        stock=book_row.get('stock', 0)
                    )
                    db.session.add(book)
            
            db.session.commit()
            print(f"✅ Migrated {len(books)} books")
            
            # Migrate Book Images
            print("🖼️ Migrating book images...")
            cursor = sqlite_conn.execute("SELECT * FROM book_images")
            images = cursor.fetchall()
            
            for image_row in images:
                existing_image = BookImage.query.filter_by(image_id=image_row['image_id']).first()
                if not existing_image:
                    image = BookImage(
                        image_id=image_row['image_id'],
                        book_id=image_row['book_id'],
                        image_url=image_row['image_url'],
                        is_main=bool(image_row.get('is_main', False))
                    )
                    db.session.add(image)
            
            db.session.commit()
            print(f"✅ Migrated {len(images)} book images")
            
            # Migrate Reviews
            print("⭐ Migrating reviews...")
            cursor = sqlite_conn.execute("SELECT * FROM reviews")
            reviews = cursor.fetchall()
            
            for review_row in reviews:
                existing_review = Review.query.filter_by(review_id=review_row['review_id']).first()
                if not existing_review:
                    # Parse the datetime string
                    created_at = None
                    if review_row.get('created_at'):
                        try:
                            created_at = datetime.fromisoformat(review_row['created_at'].replace('Z', '+00:00'))
                        except:
                            created_at = datetime.now()
                    
                    review = Review(
                        review_id=review_row['review_id'],
                        book_id=review_row['book_id'],
                        user_id=review_row['user_id'],
                        rating=review_row['rating'],
                        description=review_row.get('description'),
                        created_at=created_at
                    )
                    db.session.add(review)
            
            db.session.commit()
            print(f"✅ Migrated {len(reviews)} reviews")
            
            # Migrate Orders
            print("📦 Migrating orders...")
            cursor = sqlite_conn.execute("SELECT * FROM orders")
            orders = cursor.fetchall()
            
            for order_row in orders:
                existing_order = Order.query.filter_by(order_id=order_row['order_id']).first()
                if not existing_order:
                    # Parse datetime strings
                    order_date = None
                    delivery_date = None
                    
                    if order_row.get('order_date'):
                        try:
                            order_date = datetime.fromisoformat(order_row['order_date'].replace('Z', '+00:00'))
                        except:
                            order_date = datetime.now()
                    
                    if order_row.get('delivery_date'):
                        try:
                            delivery_date = datetime.fromisoformat(order_row['delivery_date'].replace('Z', '+00:00'))
                        except:
                            pass
                    
                    order = Order(
                        order_id=order_row['order_id'],
                        user_id=order_row['user_id'],
                        order_date=order_date,
                        delivery_date=delivery_date,
                        status=order_row.get('status', 'completed'),
                        subtotal=order_row.get('subtotal'),
                        delivery_charge=order_row.get('delivery_charge'),
                        total_amount=order_row.get('total_amount'),
                        shipping_address=order_row.get('shipping_address'),
                        payment_method=order_row.get('payment_method'),
                        tracking_number=order_row.get('tracking_number')
                    )
                    db.session.add(order)
            
            db.session.commit()
            print(f"✅ Migrated {len(orders)} orders")
            
            # Migrate Order Items
            print("📋 Migrating order items...")
            cursor = sqlite_conn.execute("SELECT * FROM order_items")
            order_items = cursor.fetchall()
            
            for item_row in order_items:
                existing_item = OrderItem.query.filter_by(order_item_id=item_row['order_item_id']).first()
                if not existing_item:
                    item = OrderItem(
                        order_item_id=item_row['order_item_id'],
                        order_id=item_row['order_id'],
                        book_id=item_row['book_id'],
                        quantity=item_row['quantity'],
                        price=item_row['price']
                    )
                    db.session.add(item)
            
            db.session.commit()
            print(f"✅ Migrated {len(order_items)} order items")
            
            # Migrate Cart Items (if any)
            print("🛒 Migrating cart items...")
            cursor = sqlite_conn.execute("SELECT * FROM cart_items")
            cart_items = cursor.fetchall()
            
            for cart_row in cart_items:
                existing_cart = CartItem.query.filter_by(cart_item_id=cart_row['cart_item_id']).first()
                if not existing_cart:
                    added_at = None
                    if cart_row.get('added_at'):
                        try:
                            added_at = datetime.fromisoformat(cart_row['added_at'].replace('Z', '+00:00'))
                        except:
                            added_at = datetime.now()
                    
                    cart_item = CartItem(
                        cart_item_id=cart_row['cart_item_id'],
                        user_id=cart_row['user_id'],
                        book_id=cart_row['book_id'],
                        quantity=cart_row['quantity'],
                        added_at=added_at
                    )
                    db.session.add(cart_item)
            
            db.session.commit()
            print(f"✅ Migrated {len(cart_items)} cart items")
            
            print("\n🎉 Migration completed successfully!")
            print("📊 Summary:")
            print(f"   • Users: {len(users)}")
            print(f"   • Books: {len(books)}")
            print(f"   • Book Images: {len(images)}")
            print(f"   • Reviews: {len(reviews)}")
            print(f"   • Orders: {len(orders)}")
            print(f"   • Order Items: {len(order_items)}")
            print(f"   • Cart Items: {len(cart_items)}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
        finally:
            sqlite_conn.close()

if __name__ == '__main__':
    migrate_data()
