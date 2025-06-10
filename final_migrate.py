#!/usr/bin/env python3
"""
Clean Migration Script - SQLite to MySQL
Migrates all data from SQLite to MySQL with proper error handling.
"""

import sqlite3
from model import app, db, User, Book, BookImage, Review, CartItem, Order, OrderItem
from datetime import datetime
import sys

def safe_datetime_parse(date_string):
    """Safely parse datetime strings from SQLite"""
    if not date_string:
        return None
    try:
        # Handle various datetime formats from SQLite
        if 'T' in date_string:
            date_string = date_string.replace('Z', '+00:00')
            return datetime.fromisoformat(date_string)
        else:
            # Try parsing as simple date
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    except:
        return datetime.now()

def migrate_all_data():
    """Complete migration from SQLite to MySQL"""
    
    print("🔄 Starting SQLite to MySQL Migration")
    print("=" * 50)
    
    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect('instance/shopping_site.db')
        sqlite_conn.row_factory = sqlite3.Row
        print("✅ Connected to SQLite database")
    except Exception as e:
        print(f"❌ Error connecting to SQLite: {e}")
        return False
    
    with app.app_context():
        try:
            # Test MySQL connection
            db.session.execute(db.text("SELECT 1"))
            print("✅ Connected to MySQL database")
            
            migration_stats = {}
            
            # 1. Migrate Users
            print("\n👥 Migrating users...")
            cursor = sqlite_conn.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            for user_row in users:
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
            migration_stats['users'] = len(users)
            print(f"✅ Migrated {len(users)} users")
            
            # 2. Migrate Books
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
                        price=float(book_row.get('price', 0)) if book_row.get('price') else None,
                        delivery_date=book_row.get('delivery_date'),
                        genre=book_row.get('genre'),
                        format=book_row.get('format', 'Paperback'),
                        rating_avg=float(book_row.get('rating_avg', 0.0)) if book_row.get('rating_avg') else 0.0,
                        stock=book_row.get('stock', 0)
                    )
                    db.session.add(book)
            
            db.session.commit()
            migration_stats['books'] = len(books)
            print(f"✅ Migrated {len(books)} books")
            
            # 3. Migrate Book Images
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
            migration_stats['book_images'] = len(images)
            print(f"✅ Migrated {len(images)} book images")
            
            # 4. Migrate Reviews
            print("⭐ Migrating reviews...")
            cursor = sqlite_conn.execute("SELECT * FROM reviews")
            reviews = cursor.fetchall()
            
            for review_row in reviews:
                existing_review = Review.query.filter_by(review_id=review_row['review_id']).first()
                if not existing_review:
                    review = Review(
                        review_id=review_row['review_id'],
                        book_id=review_row['book_id'],
                        user_id=review_row['user_id'],
                        rating=review_row['rating'],
                        description=review_row.get('description'),
                        created_at=safe_datetime_parse(review_row.get('created_at'))
                    )
                    db.session.add(review)
            
            db.session.commit()
            migration_stats['reviews'] = len(reviews)
            print(f"✅ Migrated {len(reviews)} reviews")
            
            # 5. Migrate Orders
            print("📦 Migrating orders...")
            cursor = sqlite_conn.execute("SELECT * FROM orders")
            orders = cursor.fetchall()
            
            for order_row in orders:
                existing_order = Order.query.filter_by(order_id=order_row['order_id']).first()
                if not existing_order:
                    order = Order(
                        order_id=order_row['order_id'],
                        user_id=order_row['user_id'],
                        order_date=safe_datetime_parse(order_row.get('order_date')),
                        delivery_date=safe_datetime_parse(order_row.get('delivery_date')),
                        status=order_row.get('status', 'completed'),
                        subtotal=float(order_row.get('subtotal', 0)) if order_row.get('subtotal') else None,
                        delivery_charge=float(order_row.get('delivery_charge', 0)) if order_row.get('delivery_charge') else None,
                        total_amount=float(order_row.get('total_amount', 0)) if order_row.get('total_amount') else None,
                        shipping_address=order_row.get('shipping_address'),
                        payment_method=order_row.get('payment_method'),
                        tracking_number=order_row.get('tracking_number')
                    )
                    db.session.add(order)
            
            db.session.commit()
            migration_stats['orders'] = len(orders)
            print(f"✅ Migrated {len(orders)} orders")
            
            # 6. Migrate Order Items
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
                        price_at_time=float(item_row.get('price_at_time', 0)) if item_row.get('price_at_time') else None
                    )
                    db.session.add(item)
            
            db.session.commit()
            migration_stats['order_items'] = len(order_items)
            print(f"✅ Migrated {len(order_items)} order items")
            
            # 7. Migrate Cart Items
            print("🛒 Migrating cart items...")
            cursor = sqlite_conn.execute("SELECT * FROM cart_items")
            cart_items = cursor.fetchall()
            
            for cart_row in cart_items:
                existing_cart = CartItem.query.filter_by(cart_item_id=cart_row['cart_item_id']).first()
                if not existing_cart:
                    cart_item = CartItem(
                        cart_item_id=cart_row['cart_item_id'],
                        user_id=cart_row['user_id'],
                        book_id=cart_row['book_id'],
                        quantity=cart_row['quantity'],
                        added_at=safe_datetime_parse(cart_row.get('added_at'))
                    )
                    db.session.add(cart_item)
            
            db.session.commit()
            migration_stats['cart_items'] = len(cart_items)
            print(f"✅ Migrated {len(cart_items)} cart items")
            
            # Final Summary
            print("\n🎉 Migration Completed Successfully!")
            print("=" * 50)
            print("📊 Migration Summary:")
            for table, count in migration_stats.items():
                print(f"   • {table.replace('_', ' ').title()}: {count:,}")
            
            total_records = sum(migration_stats.values())
            print(f"\n   🔢 Total Records Migrated: {total_records:,}")
            print(f"   🗄️  Database: SQLite → MySQL")
            print(f"   ✅ Status: Complete")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False
        finally:
            sqlite_conn.close()

if __name__ == '__main__':
    success = migrate_all_data()
    if success:
        print("\n🚀 Your bookstore is now running on MySQL!")
        print("   Next steps:")
        print("   1. Start your Flask app: python app.py")
        print("   2. Visit: http://127.0.0.1:5000")
        print("   3. All your data should be preserved!")
    else:
        print("\n❌ Migration failed. Check the error messages above.")
        sys.exit(1)
