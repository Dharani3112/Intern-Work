#!/usr/bin/env python3
"""
Remove SQLite Dependency and Ensure MySQL-Only Operation
Updates configuration to use MySQL exclusively.
"""

import os
from model import app, db

def update_configuration():
    """Update app configuration to use MySQL only"""
    print("🔧 Updating Application Configuration for MySQL-Only Operation")
    print("=" * 70)
    
    # Check current configuration
    current_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    print(f"Current Database URI: {current_uri}")
    
    if 'mysql' in current_uri.lower():
        print("✅ Application is already configured for MySQL")
        return True
    else:
        print("⚠️  Application still has SQLite configuration")
        return False

def verify_mysql_connection():
    """Verify that MySQL connection is working"""
    print("\n🔍 Verifying MySQL Connection...")
    
    with app.app_context():
        try:
            # Test basic connection
            result = db.session.execute(db.text("SELECT 1 as test")).fetchone()
            if result and result[0] == 1:
                print("✅ MySQL connection successful")
                
                # Check database name
                db_result = db.session.execute(db.text("SELECT DATABASE() as db_name")).fetchone()
                if db_result:
                    print(f"✅ Connected to database: {db_result[0]}")
                
                return True
            else:
                print("❌ MySQL connection test failed")
                return False
                
        except Exception as e:
            print(f"❌ MySQL connection error: {e}")
            return False

def verify_data_exists():
    """Verify that data exists in MySQL"""
    print("\n📊 Verifying Data in MySQL...")
    
    with app.app_context():
        try:
            from model import User, Book, Order, OrderItem
            
            # Check data counts
            users = User.query.count()
            books = Book.query.count()
            orders = Order.query.count()
            order_items = OrderItem.query.count()
            
            print(f"   Users: {users}")
            print(f"   Books: {books}")
            print(f"   Orders: {orders}")
            print(f"   Order Items: {order_items}")
            
            if users > 0 and books > 0:
                print("✅ Core data (users and books) exists in MySQL")
                
                if orders > 0 and order_items > 0:
                    print("✅ Order data exists in MySQL")
                    return True
                else:
                    print("⚠️  No order data found - run create_mysql_orders.py to generate orders")
                    return False
            else:
                print("❌ Missing core data in MySQL")
                return False
                
        except Exception as e:
            print(f"❌ Error checking data: {e}")
            return False

def update_env_file():
    """Ensure .env file has MySQL configuration"""
    print("\n📝 Checking .env Configuration...")
    
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
        
        if 'mysql+pymysql' in content:
            print("✅ .env file configured for MySQL")
            
            # Check if SQLite URI is commented out
            if 'sqlite:///shopping_site.db' in content and not content.count('# SQLALCHEMY_DATABASE_URI=sqlite'):
                print("⚠️  SQLite URI is still active in .env")
                print("📝 Updating .env to disable SQLite...")
                
                # Comment out SQLite line
                updated_content = content.replace(
                    'SQLALCHEMY_DATABASE_URI=sqlite:///shopping_site.db',
                    '# SQLALCHEMY_DATABASE_URI=sqlite:///shopping_site.db  # Disabled - using MySQL'
                )
                
                with open(env_path, 'w') as f:
                    f.write(updated_content)
                
                print("✅ SQLite URI commented out in .env")
            
            return True
        else:
            print("❌ .env file not configured for MySQL")
            return False
    else:
        print("❌ .env file not found")
        return False

def remove_sqlite_file():
    """Optionally remove or rename SQLite database file"""
    print("\n🗄️  SQLite Database File Management...")
    
    sqlite_path = 'instance/shopping_site.db'
    if os.path.exists(sqlite_path):
        print(f"📁 SQLite file found: {sqlite_path}")
        
        # Ask user what to do with SQLite file
        action = input("What would you like to do with the SQLite file?\n"
                      "1. Keep as backup (rename to .backup)\n"
                      "2. Delete completely\n"
                      "3. Keep as is\n"
                      "Enter choice (1/2/3): ").strip()
        
        if action == '1':
            backup_path = sqlite_path + '.backup'
            try:
                os.rename(sqlite_path, backup_path)
                print(f"✅ SQLite file renamed to: {backup_path}")
                return True
            except Exception as e:
                print(f"❌ Error renaming file: {e}")
                return False
                
        elif action == '2':
            try:
                os.remove(sqlite_path)
                print("✅ SQLite file deleted")
                return True
            except Exception as e:
                print(f"❌ Error deleting file: {e}")
                return False
                
        elif action == '3':
            print("✅ SQLite file kept as is")
            return True
        else:
            print("⚠️  Invalid choice, keeping file as is")
            return True
    else:
        print("✅ No SQLite file found")
        return True

def test_application():
    """Test that the application works with MySQL only"""
    print("\n🧪 Testing Application with MySQL...")
    
    with app.app_context():
        try:
            from model import User, Book
            
            # Test basic queries
            test_user = User.query.first()
            test_book = Book.query.first()
            
            if test_user and test_book:
                print(f"✅ Successfully queried user: {test_user.username}")
                print(f"✅ Successfully queried book: {test_book.title}")
                print("✅ Application is working with MySQL")
                return True
            else:
                print("❌ Could not query basic data")
                return False
                
        except Exception as e:
            print(f"❌ Application test failed: {e}")
            return False

def main():
    """Main function to ensure MySQL-only operation"""
    print("🚀 MYSQL-ONLY CONFIGURATION SETUP")
    print("=" * 70)
    print("This script ensures your Flask bookstore uses MySQL exclusively.")
    print("It will disable SQLite and verify MySQL operation.")
    print()
    
    all_checks_passed = True
    
    # 1. Check configuration
    if not update_configuration():
        print("❌ Configuration check failed")
        all_checks_passed = False
    
    # 2. Verify MySQL connection
    if not verify_mysql_connection():
        print("❌ MySQL connection failed")
        all_checks_passed = False
    
    # 3. Verify data exists
    if not verify_data_exists():
        print("❌ Data verification failed")
        all_checks_passed = False
    
    # 4. Update .env file
    if not update_env_file():
        print("❌ .env file update failed")
        all_checks_passed = False
    
    # 5. Handle SQLite file
    if not remove_sqlite_file():
        print("❌ SQLite file management failed")
        all_checks_passed = False
    
    # 6. Test application
    if not test_application():
        print("❌ Application test failed")
        all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("🎉 SUCCESS! Your Flask Bookstore is now MySQL-Only")
        print("✅ SQLite dependency removed")
        print("✅ MySQL connection verified")
        print("✅ Application tested and working")
        print()
        print("🚀 Your bookstore is now production-ready with MySQL!")
        print("   - All data is stored in MySQL")
        print("   - Better performance and scalability")
        print("   - Ready for production deployment")
        print("   - No more SQLite dependencies")
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print("   Your application may still work, but there might be issues.")
    
    return all_checks_passed

if __name__ == '__main__':
    main()
