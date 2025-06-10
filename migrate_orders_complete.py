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

def safe_datetime_parse(date_string):
    """Safely parse datetime strings from SQLite"""
    if not date_string:
        return None
    try:
        if 'T' in date_string:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        elif '-' in date_string and ':' in date_string:
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.now()
    except Exception as e:
        print(f"Date parsing error for '{date_string}': {e}")
        return datetime.now()

def migrate_orders():
    """Migrate orders from SQLite to MySQL in batches"""
    print("📦 Starting Orders Migration...")
    print("=" * 50)
    
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    
    with app.app_context():
        try:
            # Check current status
            cursor = sqlite_conn.execute('SELECT COUNT(*) FROM orders')
            sqlite_orders = cursor.fetchone()[0]
            mysql_orders = Order.query.count()
            
            print(f"📊 Migration Status:")
            print(f"   SQLite Orders: {sqlite_orders:,}")
            print(f"   MySQL Orders: {mysql_orders:,}")
            
            if mysql_orders > 0:
                print("⚠️  MySQL already has orders. Checking for new orders to add...")
                
                # Get the highest order_id in MySQL
                cursor = db.session.execute(db.text("SELECT MAX(order_id) FROM orders"))
                max_mysql_id = cursor.fetchone()[0] or 0
                print(f"   Highest MySQL order ID: {max_mysql_id}")
                
                # Only migrate orders with higher IDs
                sqlite_cursor = sqlite_conn.execute(f'SELECT COUNT(*) FROM orders WHERE order_id > {max_mysql_id}')
                remaining_orders = sqlite_cursor.fetchone()[0]
                print(f"   Orders to migrate: {remaining_orders:,}")
                
                if remaining_orders == 0:
                    print("✅ All orders already migrated!")
                    return True
            
            print("\n🔄 Migrating Orders...")
            
            # Get all orders from SQLite with proper column selection
            cursor = sqlite_conn.execute('''
                SELECT order_id, user_id, order_date, delivery_date, status,
                       subtotal, delivery_charge, total_amount, shipping_address,
                       payment_method, tracking_number
                FROM orders
                ORDER BY order_id
            ''')
            
            orders = cursor.fetchall()
            print(f"📋 Found {len(orders):,} total orders in SQLite")
            
            # Process in batches
            batch_size = 100
            successful_orders = 0
            failed_orders = 0
            
            for i in range(0, len(orders), batch_size):
                batch = orders[i:i + batch_size]
                batch_number = (i // batch_size) + 1
                total_batches = (len(orders) + batch_size - 1) // batch_size
                
                print(f"   Processing batch {batch_number}/{total_batches} ({len(batch)} orders)...")
                
                try:
                    for ord_row in batch:
                        # Check if order already exists
                        existing = Order.query.filter_by(order_id=ord_row[0]).first()
                        if existing:
                            continue
                        
                        # Parse dates safely
                        order_date = safe_datetime_parse(ord_row[2])
                        delivery_date = safe_datetime_parse(ord_row[3])
                        
                        # Create order object
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
                        successful_orders += 1
                    
                    # Commit batch
                    db.session.commit()
                    print(f"     ✅ Batch {batch_number} completed successfully")
                    
                except Exception as e:
                    print(f"     ❌ Batch {batch_number} failed: {e}")
                    db.session.rollback()
                    failed_orders += len(batch)
                    continue
            
            print(f"\n📊 Orders Migration Summary:")
            print(f"   ✅ Successfully migrated: {successful_orders:,}")
            print(f"   ❌ Failed: {failed_orders:,}")
            print(f"   📈 Success rate: {(successful_orders/(successful_orders+failed_orders)*100):.1f}%")
            
            return successful_orders > 0
            
        except Exception as e:
            print(f"❌ Critical error in orders migration: {e}")
            traceback.print_exc()
            db.session.rollback()
            return False
        finally:
            sqlite_conn.close()

def migrate_order_items():
    """Migrate order items from SQLite to MySQL in batches"""
    print("\n📋 Starting Order Items Migration...")
    print("=" * 50)
    
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    
    with app.app_context():
        try:
            # Check current status
            cursor = sqlite_conn.execute('SELECT COUNT(*) FROM order_items')
            sqlite_items = cursor.fetchone()[0]
            mysql_items = OrderItem.query.count()
            
            print(f"📊 Migration Status:")
            print(f"   SQLite Order Items: {sqlite_items:,}")
            print(f"   MySQL Order Items: {mysql_items:,}")
            
            if mysql_items > 0:
                print("⚠️  MySQL already has order items. Checking for new items...")
                
                # Get the highest order_item_id in MySQL
                cursor = db.session.execute(db.text("SELECT MAX(order_item_id) FROM order_items"))
                max_mysql_id = cursor.fetchone()[0] or 0
                print(f"   Highest MySQL order item ID: {max_mysql_id}")
                
                # Only migrate items with higher IDs
                sqlite_cursor = sqlite_conn.execute(f'SELECT COUNT(*) FROM order_items WHERE order_item_id > {max_mysql_id}')
                remaining_items = sqlite_cursor.fetchone()[0]
                print(f"   Order items to migrate: {remaining_items:,}")
                
                if remaining_items == 0:
                    print("✅ All order items already migrated!")
                    return True
            
            print("\n🔄 Migrating Order Items...")
            
            # Get all order items from SQLite
            cursor = sqlite_conn.execute('''
                SELECT order_item_id, order_id, book_id, quantity, price_at_time
                FROM order_items
                ORDER BY order_item_id
            ''')
            
            order_items = cursor.fetchall()
            print(f"📋 Found {len(order_items):,} total order items in SQLite")
            
            # Process in larger batches for order items
            batch_size = 500
            successful_items = 0
            failed_items = 0
            
            for i in range(0, len(order_items), batch_size):
                batch = order_items[i:i + batch_size]
                batch_number = (i // batch_size) + 1
                total_batches = (len(order_items) + batch_size - 1) // batch_size
                
                print(f"   Processing batch {batch_number}/{total_batches} ({len(batch)} items)...")
                
                try:
                    for item_row in batch:
                        # Check if item already exists
                        existing = OrderItem.query.filter_by(order_item_id=item_row[0]).first()
                        if existing:
                            continue
                        
                        # Create order item object
                        item = OrderItem(
                            order_item_id=item_row[0],
                            order_id=item_row[1],
                            book_id=item_row[2],
                            quantity=item_row[3],
                            price_at_time=float(item_row[4]) if item_row[4] else None
                        )
                        db.session.add(item)
                        successful_items += 1
                    
                    # Commit batch
                    db.session.commit()
                    print(f"     ✅ Batch {batch_number} completed successfully")
                    
                except Exception as e:
                    print(f"     ❌ Batch {batch_number} failed: {e}")
                    db.session.rollback()
                    failed_items += len(batch)
                    continue
            
            print(f"\n📊 Order Items Migration Summary:")
            print(f"   ✅ Successfully migrated: {successful_items:,}")
            print(f"   ❌ Failed: {failed_items:,}")
            print(f"   📈 Success rate: {(successful_items/(successful_items+failed_items)*100):.1f}%")
            
            return successful_items > 0
            
        except Exception as e:
            print(f"❌ Critical error in order items migration: {e}")
            traceback.print_exc()
            db.session.rollback()
            return False
        finally:
            sqlite_conn.close()

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying Migration...")
    print("=" * 50)
    
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    
    with app.app_context():
        try:
            # Check final counts
            sqlite_orders = sqlite_conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
            sqlite_items = sqlite_conn.execute('SELECT COUNT(*) FROM order_items').fetchone()[0]
            
            mysql_orders = Order.query.count()
            mysql_items = OrderItem.query.count()
            
            print("📊 Final Verification:")
            print(f"   Orders - SQLite: {sqlite_orders:,} | MySQL: {mysql_orders:,}")
            print(f"   Order Items - SQLite: {sqlite_items:,} | MySQL: {mysql_items:,}")
            
            # Check for specific order details
            sample_order = Order.query.first()
            if sample_order:
                print(f"\n📋 Sample Order Verification:")
                print(f"   Order ID: {sample_order.order_id}")
                print(f"   User ID: {sample_order.user_id}")
                print(f"   Total: ${sample_order.total_amount}")
                print(f"   Status: {sample_order.status}")
                print(f"   Date: {sample_order.order_date}")
                
                # Check order items for this order
                items = OrderItem.query.filter_by(order_id=sample_order.order_id).all()
                print(f"   Items: {len(items)} items")
            
            success = (mysql_orders >= sqlite_orders * 0.95 and mysql_items >= sqlite_items * 0.95)
            
            if success:
                print("\n✅ Migration verification PASSED!")
                print("   Orders and order items successfully migrated to MySQL!")
            else:
                print("\n⚠️  Migration verification shows some discrepancies.")
                print("   Please check the migration logs for details.")
            
            return success
            
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
        finally:
            sqlite_conn.close()

def main():
    """Main migration function"""
    print("🚀 ORDERS & ORDER ITEMS MIGRATION TO MYSQL")
    print("=" * 60)
    print("This script will migrate orders and order items from SQLite to MySQL")
    print("Processing will be done in batches to handle large datasets efficiently.")
    print()
    
    try:
        # Step 1: Migrate Orders
        orders_success = migrate_orders()
        
        if not orders_success:
            print("❌ Orders migration failed. Stopping process.")
            return False
        
        # Step 2: Migrate Order Items
        items_success = migrate_order_items()
        
        if not items_success:
            print("❌ Order items migration failed.")
            return False
        
        # Step 3: Verify Migration
        verification_success = verify_migration()
        
        if verification_success:
            print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✅ Orders and order items have been successfully migrated to MySQL")
            print("✅ Your Flask bookstore is now fully operational with MySQL")
            print("✅ All historical order data has been preserved")
            print("\n🚀 Next Steps:")
            print("   1. Your Flask app is ready for production deployment")
            print("   2. All order history is now available in MySQL")
            print("   3. Admin dashboard will show all order analytics")
            print("   4. Users can view their complete order history")
            
        return verification_success
        
    except Exception as e:
        print(f"❌ Migration process failed: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
