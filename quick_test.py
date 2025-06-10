#!/usr/bin/env python3
"""
Simple Step-by-Step Migration
"""

import sqlite3
from model import app, db, User, Book, BookImage, Review, CartItem, Order, OrderItem
from datetime import datetime

def test_migration():
    print("🔄 Testing Migration Components...")
    
    # Test SQLite
    try:
        sqlite_conn = sqlite3.connect('instance/shopping_site.db')
        sqlite_conn.row_factory = sqlite3.Row
        cursor = sqlite_conn.execute('SELECT COUNT(*) FROM users')
        sqlite_users = cursor.fetchone()[0]
        print(f"✅ SQLite: {sqlite_users} users found")
        sqlite_conn.close()
    except Exception as e:
        print(f"❌ SQLite error: {e}")
        return False
    
    # Test MySQL
    try:
        with app.app_context():
            mysql_users = User.query.count()
            print(f"✅ MySQL: {mysql_users} users found")
    except Exception as e:
        print(f"❌ MySQL error: {e}")
        return False
    
    print("✅ All components working!")
    return True

def migrate_users_only():
    print("\n👥 Migrating Users Only...")
    
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    sqlite_conn.row_factory = sqlite3.Row
    
    with app.app_context():
        try:
            cursor = sqlite_conn.execute("SELECT * FROM users LIMIT 5")
            users = cursor.fetchall()
            
            added_count = 0
            for user_row in users:
                existing = User.query.filter_by(user_id=user_row['user_id']).first()
                if not existing:
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
                    added_count += 1
            
            db.session.commit()
            print(f"✅ Added {added_count} users to MySQL")
            print(f"✅ Total MySQL users: {User.query.count()}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        finally:
            sqlite_conn.close()

if __name__ == '__main__':
    if test_migration():
        migrate_users_only()
    else:
        print("❌ Component test failed!")
