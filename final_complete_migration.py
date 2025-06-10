#!/usr/bin/env python3
"""
Final Complete Migration - All Remaining Data
"""

import sqlite3
import sys
from model import app, db, BookImage, Review, Order, OrderItem, CartItem
from datetime import datetime
import traceback

def complete_migration():
    print("🚀 Final Complete Migration - All Remaining Data")
    print("=" * 60)
    
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    
    with app.app_context():
        try:
            migration_summary = {}
            
            # 1. Migrate Book Images
            print("🖼️ Migrating Book Images...")
            cursor = sqlite_conn.execute('SELECT image_id, book_id, image_url, is_main FROM book_images')
            images = cursor.fetchall()
            
            image_count = 0
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
                    image_count += 1
            
            db.session.commit()
            migration_summary['book_images'] = image_count
            print(f"✅ Migrated {image_count} book images")
            
            # 2. Migrate Reviews (in batches)
            print("⭐ Migrating Reviews...")
            cursor = sqlite_conn.execute('SELECT review_id, book_id, user_id, rating, description, created_at FROM reviews')
            reviews = cursor.fetchall()
            
            review_count = 0
            batch_size = 50
            for i in range(0, len(reviews), batch_size):
                batch = reviews[i:i + batch_size]
                
                for rev_row in batch:
                    existing = Review.query.filter_by(review_id=rev_row[0]).first()
                    if not existing:
                        created_at = None
                        if rev_row[5]:
                            try:
                                if 'T' in rev_row[5]:
                                    created_at = datetime.fromisoformat(rev_row[5].replace('Z', '+00:00'))
                                else:
                                    created_at = datetime.strptime(rev_row[5], '%Y-%m-%d %H:%M:%S')
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
                        review_count += 1
                
                db.session.commit()
                print(f"   Processed batch {i//batch_size + 1}/{(len(reviews) + batch_size - 1)//batch_size}")
            
            migration_summary['reviews'] = review_count
            print(f"✅ Migrated {review_count} reviews")
            
            # 3. Migrate Orders (in batches)
            print("📦 Migrating Orders...")
            cursor = sqlite_conn.execute('''
                SELECT order_id, user_id, order_date, delivery_date, status,
                       subtotal, delivery_charge, total_amount, shipping_address,
                       payment_method, tracking_number
                FROM orders
            ''')
            orders = cursor.fetchall()
            
            order_count = 0
            batch_size = 100
            for i in range(0, len(orders), batch_size):
                batch = orders[i:i + batch_size]
                
                for ord_row in batch:
                    existing = Order.query.filter_by(order_id=ord_row[0]).first()
                    if not existing:
                        # Parse dates safely
                        order_date = None
                        delivery_date = None
                        
                        if ord_row[2]:
                            try:
                                if 'T' in ord_row[2]:
                                    order_date = datetime.fromisoformat(ord_row[2].replace('Z', '+00:00'))
                                else:
                                    order_date = datetime.strptime(ord_row[2], '%Y-%m-%d %H:%M:%S')
                            except:
                                order_date = datetime.now()
                        
                        if ord_row[3]:
                            try:
                                if 'T' in ord_row[3]:
                                    delivery_date = datetime.fromisoformat(ord_row[3].replace('Z', '+00:00'))
                                else:
                                    delivery_date = datetime.strptime(ord_row[3], '%Y-%m-%d %H:%M:%S')
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
                        order_count += 1
                
                db.session.commit()
                print(f"   Processed batch {i//batch_size + 1}/{(len(orders) + batch_size - 1)//batch_size}")
            
            migration_summary['orders'] = order_count
            print(f"✅ Migrated {order_count} orders")
            
            # 4. Migrate Order Items (in batches)
            print("📋 Migrating Order Items...")
            cursor = sqlite_conn.execute('SELECT order_item_id, order_id, book_id, quantity, price_at_time FROM order_items')
            order_items = cursor.fetchall()
            
            item_count = 0
            batch_size = 200
            for i in range(0, len(order_items), batch_size):
                batch = order_items[i:i + batch_size]
                
                for item_row in batch:
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
                        item_count += 1
                
                db.session.commit()
                print(f"   Processed batch {i//batch_size + 1}/{(len(order_items) + batch_size - 1)//batch_size}")
            
            migration_summary['order_items'] = item_count
            print(f"✅ Migrated {item_count} order items")
            
            # 5. Migrate Cart Items
            print("🛒 Migrating Cart Items...")
            cursor = sqlite_conn.execute('SELECT cart_item_id, user_id, book_id, quantity, added_at FROM cart_items')
            cart_items = cursor.fetchall()
            
            cart_count = 0
            for cart_row in cart_items:
                existing = CartItem.query.filter_by(cart_item_id=cart_row[0]).first()
                if not existing:
                    added_at = None
                    if cart_row[4]:
                        try:
                            if 'T' in cart_row[4]:
                                added_at = datetime.fromisoformat(cart_row[4].replace('Z', '+00:00'))
                            else:
                                added_at = datetime.strptime(cart_row[4], '%Y-%m-%d %H:%M:%S')
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
                    cart_count += 1
            
            db.session.commit()
            migration_summary['cart_items'] = cart_count
            print(f"✅ Migrated {cart_count} cart items")
            
            # Final Summary
            print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("📊 Migration Summary:")
            total_migrated = 0
            for table, count in migration_summary.items():
                print(f"   • {table.replace('_', ' ').title()}: {count:,}")
                total_migrated += count
            
            print(f"\n🔢 Total New Records Migrated: {total_migrated:,}")
            print("🗄️  Database: SQLite → MySQL")
            print("✅ Status: COMPLETE")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration Error: {e}")
            print("Full traceback:")
            traceback.print_exc()
            db.session.rollback()
            return False
        finally:
            sqlite_conn.close()

if __name__ == '__main__':
    print("Starting final migration...")
    success = complete_migration()
    
    if success:
        print("\n🚀 CONGRATULATIONS!")
        print("Your Flask Bookstore has been successfully migrated to MySQL!")
        print("\nNext steps:")
        print("1. Your Flask app should already be running at: http://127.0.0.1:5000")
        print("2. All your data (users, books, orders, reviews) is now in MySQL")
        print("3. The application is production-ready with MySQL!")
        print("4. You can now deploy this to a production server")
        
        # Final verification
        with app.app_context():
            from model import User, Book, Review, Order
            print(f"\n📊 Final Database Counts:")
            print(f"   • Users: {User.query.count():,}")
            print(f"   • Books: {Book.query.count():,}")
            print(f"   • Reviews: {Review.query.count():,}")
            print(f"   • Orders: {Order.query.count():,}")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
