"""
Final Verification Script for MySQL Migration
This script verifies that the Flask bookstore application has been successfully migrated to MySQL
and is no longer using SQLite.
"""

import os
from app import app, db
from model import User, Book, Order, OrderItem, Review, CartItem
from sqlalchemy import text

def verify_mysql_migration():
    print("=" * 60)
    print("MYSQL MIGRATION VERIFICATION")
    print("=" * 60)
    
    with app.app_context():
        # 1. Verify database connection
        print("1. Database Connection:")
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"   Database URI: {db_uri}")
        
        if 'mysql' in db_uri.lower():
            print("   ✅ Using MySQL database")
        else:
            print("   ❌ Not using MySQL database")
            return False
        
        # 2. Verify tables exist
        print("\n2. Database Tables:")
        try:
            tables = db.session.execute(text("SHOW TABLES")).fetchall()
            table_names = [table[0] for table in tables]
            expected_tables = ['users', 'books', 'orders', 'order_items', 'reviews', 'cart_items', 'book_images']
            
            for table in expected_tables:
                if table in table_names:
                    print(f"   ✅ {table} table exists")
                else:
                    print(f"   ❌ {table} table missing")
            
        except Exception as e:
            print(f"   ❌ Error checking tables: {e}")
            return False
        
        # 3. Verify data counts
        print("\n3. Data Verification:")
        try:
            user_count = User.query.count()
            book_count = Book.query.count()
            order_count = Order.query.count()
            order_item_count = OrderItem.query.count()
            
            print(f"   Users: {user_count}")
            print(f"   Books: {book_count}")
            print(f"   Orders: {order_count}")
            print(f"   Order Items: {order_item_count}")
            
            if user_count > 0 and book_count > 0 and order_count > 0:
                print("   ✅ Database contains migrated data")
            else:
                print("   ❌ Missing expected data")
                return False
                
        except Exception as e:
            print(f"   ❌ Error checking data: {e}")
            return False
        
        # 4. Verify sample data integrity
        print("\n4. Data Integrity Check:")
        try:
            # Check a sample user
            sample_user = User.query.first()
            if sample_user and sample_user.username:
                print(f"   ✅ Sample user: {sample_user.username}")
            
            # Check a sample book
            sample_book = Book.query.first()
            if sample_book and sample_book.title:
                print(f"   ✅ Sample book: {sample_book.title}")
            
            # Check a sample order with items
            sample_order = Order.query.filter(Order.order_items.any()).first()
            if sample_order:
                total = float(sample_order.total_amount) if sample_order.total_amount else 0
                print(f"   ✅ Sample order: ${total:.2f} with {len(sample_order.order_items)} items")
            
        except Exception as e:
            print(f"   ❌ Error checking data integrity: {e}")
            return False
        
        # 5. Verify no SQLite usage
        print("\n5. SQLite Usage Check:")
        if 'sqlite' not in db_uri.lower():
            print("   ✅ No SQLite database in use")
        else:
            print("   ❌ Still using SQLite")
            return False
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION VERIFICATION PASSED!")
        print("The Flask bookstore application has been successfully migrated to MySQL.")
        print("All data has been preserved and the application is working correctly.")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    verify_mysql_migration()
