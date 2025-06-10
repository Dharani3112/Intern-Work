#!/usr/bin/env python3
"""
Complete Migration Script - SQLite to MySQL
"""

import sqlite3
import sys
from model import app, db, User, Book, BookImage, Review, CartItem, Order, OrderItem
from datetime import datetime

def safe_datetime(date_str):
    """Safely convert datetime string"""
    if not date_str:
        return None
    try:
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except:
        return datetime.now()

def migrate_all():
    print("🔄 Starting Complete Migration - SQLite to MySQL")
    print("=" * 60)
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    
    with app.app_context():
        try:
            # Check current state
            sqlite_users = sqlite_conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            mysql_users = User.query.count()
            
            print(f"📊 Current State:")
            print(f"   SQLite Users: {sqlite_users}")
            print(f"   MySQL Users: {mysql_users}")
            
            if mysql_users > 0:
                print("⚠️  MySQL already has data. Skipping migration.")
                return True
            
            # 1. Migrate Users
            print("\n👥 Migrating Users...")
            cursor = sqlite_conn.execute('''
                SELECT user_id, username, email, password_hash, 
                       first_name, last_name, mobile_number 
                FROM users
            ''')
            users = cursor.fetchall()
            
            for user_row in users:
                user = User(
                    user_id=user_row[0],
                    username=user_row[1],
                    email=user_row[2],
                    password_hash=user_row[3],
                    first_name=user_row[4],
                    last_name=user_row[5],
                    mobile_number=user_row[6]
                )
                db.session.add(user)
            
            db.session.commit()
            print(f"✅ Migrated {len(users)} users")
            
            # 2. Migrate Books
            print("📚 Migrating Books...")
            cursor = sqlite_conn.execute('''
                SELECT book_id, title, author, isbn, publisher, publication_year,
                       pages, language, description, price, delivery_date,
                       genre, format, rating_avg, stock
                FROM books
            ''')
            books = cursor.fetchall()
            
            for book_row in books:
                book = Book(
                    book_id=book_row[0],
                    title=book_row[1],
                    author=book_row[2],
                    isbn=book_row[3],
                    publisher=book_row[4],
                    publication_year=book_row[5],
                    pages=book_row[6],
                    language=book_row[7] or 'English',
                    description=book_row[8],
                    price=float(book_row[9]) if book_row[9] else None,
                    delivery_date=book_row[10],
                    genre=book_row[11],
                    format=book_row[12] or 'Paperback',
                    rating_avg=float(book_row[13]) if book_row[13] else 0.0,
                    stock=book_row[14] or 0
                )
                db.session.add(book)
            
            db.session.commit()
            print(f"✅ Migrated {len(books)} books")
            
            # 3. Migrate Book Images
            print("🖼️ Migrating Book Images...")
            cursor = sqlite_conn.execute('''
                SELECT image_id, book_id, image_url, is_main
                FROM book_images
            ''')
            images = cursor.fetchall()
            
            for img_row in images:
                image = BookImage(
                    image_id=img_row[0],
                    book_id=img_row[1],
                    image_url=img_row[2],
                    is_main=bool(img_row[3])
                )
                db.session.add(image)
            
            db.session.commit()
            print(f"✅ Migrated {len(images)} book images")
            
            # 4. Migrate Reviews
            print("⭐ Migrating Reviews...")
            cursor = sqlite_conn.execute('''
                SELECT review_id, book_id, user_id, rating, description, created_at
                FROM reviews
            ''')
            reviews = cursor.fetchall()
            
            for rev_row in reviews:
                review = Review(
                    review_id=rev_row[0],
                    book_id=rev_row[1],
                    user_id=rev_row[2],
                    rating=rev_row[3],
                    description=rev_row[4],
                    created_at=safe_datetime(rev_row[5])
                )
                db.session.add(review)
            
            db.session.commit()
            print(f"✅ Migrated {len(reviews)} reviews")
            
            # 5. Migrate Orders
            print("📦 Migrating Orders...")
            cursor = sqlite_conn.execute('''
                SELECT order_id, user_id, order_date, delivery_date, status,
                       subtotal, delivery_charge, total_amount, shipping_address,
                       payment_method, tracking_number
                FROM orders
            ''')
            orders = cursor.fetchall()
            
            for ord_row in orders:
                order = Order(
                    order_id=ord_row[0],
                    user_id=ord_row[1],
                    order_date=safe_datetime(ord_row[2]),
                    delivery_date=safe_datetime(ord_row[3]),
                    status=ord_row[4] or 'completed',
                    subtotal=float(ord_row[5]) if ord_row[5] else None,
                    delivery_charge=float(ord_row[6]) if ord_row[6] else None,
                    total_amount=float(ord_row[7]) if ord_row[7] else None,
                    shipping_address=ord_row[8],
                    payment_method=ord_row[9],
                    tracking_number=ord_row[10]
                )
                db.session.add(order)
            
            db.session.commit()
            print(f"✅ Migrated {len(orders)} orders")
            
            # 6. Migrate Order Items
            print("📋 Migrating Order Items...")
            cursor = sqlite_conn.execute('''
                SELECT order_item_id, order_id, book_id, quantity, price_at_time
                FROM order_items
            ''')
            order_items = cursor.fetchall()
            
            for item_row in order_items:
                item = OrderItem(
                    order_item_id=item_row[0],
                    order_id=item_row[1],
                    book_id=item_row[2],
                    quantity=item_row[3],
                    price_at_time=float(item_row[4]) if item_row[4] else None
                )
                db.session.add(item)
            
            db.session.commit()
            print(f"✅ Migrated {len(order_items)} order items")
            
            # 7. Migrate Cart Items
            print("🛒 Migrating Cart Items...")
            cursor = sqlite_conn.execute('''
                SELECT cart_item_id, user_id, book_id, quantity, added_at
                FROM cart_items
            ''')
            cart_items = cursor.fetchall()
            
            for cart_row in cart_items:
                cart_item = CartItem(
                    cart_item_id=cart_row[0],
                    user_id=cart_row[1],
                    book_id=cart_row[2],
                    quantity=cart_row[3],
                    added_at=safe_datetime(cart_row[4])
                )
                db.session.add(cart_item)
            
            db.session.commit()
            print(f"✅ Migrated {len(cart_items)} cart items")
            
            # Final Summary
            print("\n🎉 Migration Completed Successfully!")
            print("=" * 60)
            print("📊 Final Summary:")
            print(f"   • Users: {len(users):,}")
            print(f"   • Books: {len(books):,}")
            print(f"   • Book Images: {len(images):,}")
            print(f"   • Reviews: {len(reviews):,}")
            print(f"   • Orders: {len(orders):,}")
            print(f"   • Order Items: {len(order_items):,}")
            print(f"   • Cart Items: {len(cart_items):,}")
            
            total = len(users) + len(books) + len(images) + len(reviews) + len(orders) + len(order_items) + len(cart_items)
            print(f"\n🔢 Total Records Migrated: {total:,}")
            print("🗄️  Database: SQLite → MySQL")
            print("✅ Status: Complete")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False
        finally:
            sqlite_conn.close()

if __name__ == '__main__':
    success = migrate_all()
    if success:
        print("\n🚀 Your bookstore is now running on MySQL!")
        print("   Next steps:")
        print("   1. Start your Flask app: python app.py")
        print("   2. Visit: http://127.0.0.1:5000")
        print("   3. All your data should be preserved!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
