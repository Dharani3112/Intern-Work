#!/usr/bin/env python3
"""
Step-by-step Migration Script
"""

import sqlite3
from model import app, db, User, Book, BookImage, Review, CartItem, Order, OrderItem
from datetime import datetime

def migrate_users():
    """Migrate just users first"""
    print("👥 Migrating users...")
    
    sqlite_conn = sqlite3.connect('instance/shopping_site.db')
    sqlite_conn.row_factory = sqlite3.Row
    
    with app.app_context():
        try:
            cursor = sqlite_conn.execute("SELECT * FROM users LIMIT 5")
            users = cursor.fetchall()
            
            print(f"Found {len(users)} users to migrate")
            
            for user_row in users:
                print(f"Processing user: {user_row['username']}")
                
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
                    print(f"Added user: {user.username}")
                else:
                    print(f"User already exists: {existing_user.username}")
            
            db.session.commit()
            print("✅ Users migrated successfully!")
            
        except Exception as e:
            print(f"❌ Error migrating users: {e}")
            db.session.rollback()
        finally:
            sqlite_conn.close()

if __name__ == '__main__':
    migrate_users()
