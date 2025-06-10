#!/usr/bin/env python3
"""
Migration Status Check and Completion
"""

import sqlite3
from model import app, db, BookImage, Review, Order, OrderItem, CartItem
from datetime import datetime

def check_and_complete_migration():
    print("🔍 Checking Migration Status and Completing Remaining Tables")
    print("=" * 70)
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    
    with app.app_context():
        # Check what's left to migrate
        tables_to_check = [
            ('book_images', BookImage),
            ('reviews', Review),  
            ('orders', Order),
            ('order_items', OrderItem),
            ('cart_items', CartItem)
        ]
        
        for table_name, model_class in tables_to_check:
            try:
                # Count in SQLite
                cursor = sqlite_conn.execute(f'SELECT COUNT(*) FROM {table_name}')
                sqlite_count = cursor.fetchone()[0]
                
                # Count in MySQL
                mysql_count = model_class.query.count()
                
                print(f"📊 {table_name.replace('_', ' ').title()}:")
                print(f"   SQLite: {sqlite_count:,} | MySQL: {mysql_count:,}")
                
                if sqlite_count > mysql_count:
                    print(f"   🔄 Migrating {sqlite_count - mysql_count} records...")
                    
                    if table_name == 'book_images':
                        migrate_book_images(sqlite_conn)
                    elif table_name == 'reviews':
                        migrate_reviews(sqlite_conn)
                    elif table_name == 'orders':
                        migrate_orders(sqlite_conn)
                    elif table_name == 'order_items':
                        migrate_order_items(sqlite_conn)
                    elif table_name == 'cart_items':
                        migrate_cart_items(sqlite_conn)
                    
                    print(f"   ✅ Migration completed")
                else:
                    print(f"   ✅ Already migrated")
                    
            except Exception as e:
                print(f"   ❌ Error checking {table_name}: {e}")
        
        print("\n🎉 Migration Status Complete!")
        
    sqlite_conn.close()

def migrate_book_images(sqlite_conn):
    cursor = sqlite_conn.execute('SELECT image_id, book_id, image_url, is_main FROM book_images')
    images = cursor.fetchall()
    
    for img_row in images:
        existing = BookImage.query.filter_by(image_id=img_row[0]).first()
        if not existing:
            image = BookImage(
                image_id=img_row[0],
                book_id=img_row[1],
                image_url=img_row[2],
                is_main=bool(img_row[3])
            )
            db.session.add(image)
    
    db.session.commit()

def migrate_reviews(sqlite_conn):
    cursor = sqlite_conn.execute('SELECT review_id, book_id, user_id, rating, description, created_at FROM reviews')
    reviews = cursor.fetchall()
    
    for rev_row in reviews:
        existing = Review.query.filter_by(review_id=rev_row[0]).first()
        if not existing:
            created_at = None
            if rev_row[5]:
                try:
                    created_at = datetime.fromisoformat(rev_row[5].replace('Z', '+00:00'))
                except:
                    created_at = datetime.now()
            
            review = Review(
                review_id=rev_row[0],
                book_id=rev_row[1],
                user_id=rev_row[2],
                rating=rev_row[3],
                description=rev_row[4],
                created_at=created_at
            )
            db.session.add(review)
    
    db.session.commit()

def migrate_orders(sqlite_conn):
    cursor = sqlite_conn.execute('''
        SELECT order_id, user_id, order_date, delivery_date, status,
               subtotal, delivery_charge, total_amount, shipping_address,
               payment_method, tracking_number
        FROM orders
    ''')
    orders = cursor.fetchall()
    
    for ord_row in orders:
        existing = Order.query.filter_by(order_id=ord_row[0]).first()
        if not existing:
            # Parse dates
            order_date = None
            delivery_date = None
            
            if ord_row[2]:
                try:
                    order_date = datetime.fromisoformat(ord_row[2].replace('Z', '+00:00'))
                except:
                    order_date = datetime.now()
            
            if ord_row[3]:
                try:
                    delivery_date = datetime.fromisoformat(ord_row[3].replace('Z', '+00:00'))
                except:
                    pass
            
            order = Order(
                order_id=ord_row[0],
                user_id=ord_row[1],
                order_date=order_date,
                delivery_date=delivery_date,
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

def migrate_order_items(sqlite_conn):
    cursor = sqlite_conn.execute('SELECT order_item_id, order_id, book_id, quantity, price_at_time FROM order_items')
    items = cursor.fetchall()
    
    for item_row in items:
        existing = OrderItem.query.filter_by(order_item_id=item_row[0]).first()
        if not existing:
            item = OrderItem(
                order_item_id=item_row[0],
                order_id=item_row[1],
                book_id=item_row[2],
                quantity=item_row[3],
                price_at_time=float(item_row[4]) if item_row[4] else None
            )
            db.session.add(item)
    
    db.session.commit()

def migrate_cart_items(sqlite_conn):
    cursor = sqlite_conn.execute('SELECT cart_item_id, user_id, book_id, quantity, added_at FROM cart_items')
    items = cursor.fetchall()
    
    for cart_row in items:
        existing = CartItem.query.filter_by(cart_item_id=cart_row[0]).first()
        if not existing:
            added_at = None
            if cart_row[4]:
                try:
                    added_at = datetime.fromisoformat(cart_row[4].replace('Z', '+00:00'))
                except:
                    added_at = datetime.now()
            
            cart_item = CartItem(
                cart_item_id=cart_row[0],
                user_id=cart_row[1],
                book_id=cart_row[2],
                quantity=cart_row[3],
                added_at=added_at
            )
            db.session.add(cart_item)
    
    db.session.commit()

if __name__ == '__main__':
    check_and_complete_migration()
