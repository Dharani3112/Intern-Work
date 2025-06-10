#!/usr/bin/env python3
"""
MySQL Database Setup Script
Sets up the MySQL database for the bookstore application.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_mysql_database():
    """Setup MySQL database and user"""
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'database': os.getenv('MYSQL_DATABASE', 'bookstore_db'),
        'user': os.getenv('MYSQL_USERNAME', 'bookstore_user'),
        'password': os.getenv('MYSQL_PASSWORD', 'your_secure_password_here')
    }
    
    print("🔧 MySQL Database Setup")
    print("=" * 30)
    print(f"Host: {mysql_config['host']}:{mysql_config['port']}")
    print(f"Database: {mysql_config['database']}")
    print(f"User: {mysql_config['user']}")
    
    # Get root password
    root_password = input("\nEnter MySQL root password: ")
    
    try:
        # Connect as root
        connection = mysql.connector.connect(
            host=mysql_config['host'],
            port=mysql_config['port'],
            user='root',
            password=root_password
        )
        
        cursor = connection.cursor()
        
        # Create database
        print(f"\n📅 Creating database '{mysql_config['database']}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_config['database']} "
                      f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # Create user
        print(f"👤 Creating user '{mysql_config['user']}'...")
        cursor.execute(f"CREATE USER IF NOT EXISTS '{mysql_config['user']}'@'localhost' "
                      f"IDENTIFIED BY '{mysql_config['password']}'")
        
        # Grant privileges
        print(f"🔑 Granting privileges...")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {mysql_config['database']}.* "
                      f"TO '{mysql_config['user']}'@'localhost'")
        
        cursor.execute("FLUSH PRIVILEGES")
        
        print("✅ MySQL database setup completed successfully!")
        
        # Test connection with new user
        print(f"\n🧪 Testing connection with user '{mysql_config['user']}'...")
        test_connection = mysql.connector.connect(**mysql_config)
        test_cursor = test_connection.cursor()
        test_cursor.execute("SELECT 1")
        result = test_cursor.fetchone()
        
        if result:
            print("✅ Connection test successful!")
        
        test_connection.close()
        connection.close()
        
        print(f"\n📝 Database setup complete! You can now:")
        print(f"   1. Run the migration script: python migrate_to_mysql.py")
        print(f"   2. Or create new tables: python model.py")
        
        return True
        
    except Error as e:
        print(f"❌ Error setting up MySQL database: {e}")
        return False

if __name__ == '__main__':
    setup_mysql_database()
