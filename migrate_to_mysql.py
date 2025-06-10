#!/usr/bin/env python3
"""
SQLite to MySQL Migration Script
Migrates the bookstore database from SQLite to MySQL while preserving all data.
"""

import os
import sys
import sqlite3
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseMigrator:
    def __init__(self):
        self.sqlite_db = 'instance/shopping_site.db'
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USERNAME', 'bookstore_user'),
            'password': os.getenv('MYSQL_PASSWORD', 'your_secure_password_here'),
            'database': os.getenv('MYSQL_DATABASE', 'bookstore_db'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci'
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('migration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_sqlite_exists(self):
        """Check if SQLite database exists and has data"""
        if not os.path.exists(self.sqlite_db):
            self.logger.error(f"SQLite database not found at: {self.sqlite_db}")
            return False
        
        try:
            conn = sqlite3.connect(self.sqlite_db)
            cursor = conn.cursor()
            
            # Check if tables exist and have data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if not tables:
                self.logger.error("No tables found in SQLite database")
                return False
            
            # Check for key tables
            table_names = [table[0] for table in tables]
            required_tables = ['users', 'books', 'orders', 'order_items']
            
            for table in required_tables:
                if table not in table_names:
                    self.logger.error(f"Required table '{table}' not found")
                    return False
            
            # Check data counts
            cursor.execute("SELECT COUNT(*) FROM books")
            book_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            
            self.logger.info(f"SQLite database found with {book_count} books and {order_count} orders")
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking SQLite database: {e}")
            return False

    def create_mysql_database(self):
        """Create MySQL database and user if they don't exist"""
        try:
            # Connect to MySQL server without database
            connection = mysql.connector.connect(
                host=self.mysql_config['host'],
                port=self.mysql_config['port'],
                user='root',  # Assuming root access to create database
                password=input("Enter MySQL root password: ")
            )
            
            cursor = connection.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.mysql_config['database']} "
                          f"CHARACTER SET {self.mysql_config['charset']} "
                          f"COLLATE {self.mysql_config['collation']}")
            
            # Create user and grant privileges
            cursor.execute(f"CREATE USER IF NOT EXISTS '{self.mysql_config['user']}'@'localhost' "
                          f"IDENTIFIED BY '{self.mysql_config['password']}'")
            
            cursor.execute(f"GRANT ALL PRIVILEGES ON {self.mysql_config['database']}.* "
                          f"TO '{self.mysql_config['user']}'@'localhost'")
            
            cursor.execute("FLUSH PRIVILEGES")
            
            self.logger.info(f"MySQL database '{self.mysql_config['database']}' created successfully")
            connection.close()
            return True
            
        except Error as e:
            self.logger.error(f"Error creating MySQL database: {e}")
            return False

    def create_mysql_tables(self):
        """Create MySQL tables with the same structure as SQLite"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            cursor = connection.cursor()
            
            # Create tables in dependency order
            tables = {
                'users': '''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        mobile_number VARCHAR(15) NOT NULL,
                        password_hash VARCHAR(200) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'books': '''
                    CREATE TABLE IF NOT EXISTS books (
                        book_id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(200) NOT NULL,
                        author VARCHAR(200) NOT NULL,
                        genre VARCHAR(100) NOT NULL,
                        isbn VARCHAR(13) UNIQUE NOT NULL,
                        price DECIMAL(10,2) NOT NULL,
                        stock_quantity INT NOT NULL DEFAULT 0,
                        publication_year INT,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'book_images': '''
                    CREATE TABLE IF NOT EXISTS book_images (
                        image_id INT AUTO_INCREMENT PRIMARY KEY,
                        book_id INT NOT NULL,
                        image_url VARCHAR(500) NOT NULL,
                        is_main BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                    )
                ''',
                'reviews': '''
                    CREATE TABLE IF NOT EXISTS reviews (
                        review_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        book_id INT NOT NULL,
                        rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                        comment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                    )
                ''',
                'cart_items': '''
                    CREATE TABLE IF NOT EXISTS cart_items (
                        cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        book_id INT NOT NULL,
                        quantity INT DEFAULT 1,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                        FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                    )
                ''',
                'orders': '''
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_amount DECIMAL(10,2) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        shipping_address TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                ''',
                'order_items': '''
                    CREATE TABLE IF NOT EXISTS order_items (
                        order_item_id INT AUTO_INCREMENT PRIMARY KEY,
                        order_id INT NOT NULL,
                        book_id INT NOT NULL,
                        quantity INT NOT NULL,
                        price_at_time DECIMAL(10,2),
                        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                        FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
                    )
                '''
            }
            
            for table_name, create_sql in tables.items():
                cursor.execute(create_sql)
                self.logger.info(f"Created table: {table_name}")
            
            connection.commit()
            connection.close()
            return True
            
        except Error as e:
            self.logger.error(f"Error creating MySQL tables: {e}")
            return False

    def migrate_data(self):
        """Migrate data from SQLite to MySQL"""
        try:
            # Connect to both databases
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
            sqlite_cursor = sqlite_conn.cursor()
            
            mysql_conn = mysql.connector.connect(**self.mysql_config)
            mysql_cursor = mysql_conn.cursor()
            
            # Migration order (respecting foreign key dependencies)
            migration_order = [
                ('users', 'user_id'),
                ('books', 'book_id'),
                ('book_images', 'image_id'),
                ('reviews', 'review_id'),
                ('cart_items', 'cart_item_id'),
                ('orders', 'order_id'),
                ('order_items', 'order_item_id')
            ]
            
            for table_name, id_column in migration_order:
                self.logger.info(f"Migrating {table_name}...")
                
                # Get data from SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table_name}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    self.logger.info(f"No data found in {table_name}, skipping...")
                    continue
                
                # Get column names
                columns = [description[0] for description in sqlite_cursor.description]
                
                # Prepare INSERT statement
                placeholders = ', '.join(['%s'] * len(columns))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                # Convert rows to tuples
                data_tuples = [tuple(row) for row in rows]
                
                # Insert data into MySQL
                mysql_cursor.executemany(insert_sql, data_tuples)
                mysql_conn.commit()
                
                self.logger.info(f"Migrated {len(data_tuples)} records to {table_name}")
            
            sqlite_conn.close()
            mysql_conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error migrating data: {e}")
            return False

    def verify_migration(self):
        """Verify that migration was successful"""
        try:
            # Connect to both databases
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            sqlite_cursor = sqlite_conn.cursor()
            
            mysql_conn = mysql.connector.connect(**self.mysql_config)
            mysql_cursor = mysql_conn.cursor()
            
            tables = ['users', 'books', 'book_images', 'reviews', 'cart_items', 'orders', 'order_items']
            
            verification_passed = True
            
            for table in tables:
                # Count records in SQLite
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # Count records in MySQL
                mysql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                mysql_count = mysql_cursor.fetchone()[0]
                
                if sqlite_count == mysql_count:
                    self.logger.info(f"✅ {table}: {sqlite_count} records (matched)")
                else:
                    self.logger.error(f"❌ {table}: SQLite={sqlite_count}, MySQL={mysql_count} (mismatch)")
                    verification_passed = False
            
            sqlite_conn.close()
            mysql_conn.close()
            
            return verification_passed
            
        except Exception as e:
            self.logger.error(f"Error verifying migration: {e}")
            return False

    def run_migration(self):
        """Run the complete migration process"""
        self.logger.info("Starting SQLite to MySQL migration...")
        
        # Step 1: Check SQLite database
        if not self.check_sqlite_exists():
            return False
        
        # Step 2: Create MySQL database
        print("\n🔧 Creating MySQL database...")
        if not self.create_mysql_database():
            return False
        
        # Step 3: Create tables
        print("\n🏗️  Creating MySQL tables...")
        if not self.create_mysql_tables():
            return False
        
        # Step 4: Migrate data
        print("\n📦 Migrating data...")
        if not self.migrate_data():
            return False
        
        # Step 5: Verify migration
        print("\n✅ Verifying migration...")
        if not self.verify_migration():
            self.logger.warning("Migration verification failed!")
            return False
        
        self.logger.info("🎉 Migration completed successfully!")
        return True

def main():
    print("🔄 SQLite to MySQL Migration Tool")
    print("=" * 50)
    
    migrator = DatabaseMigrator()
    
    # Show configuration
    print(f"📍 SQLite Database: {migrator.sqlite_db}")
    print(f"📍 MySQL Host: {migrator.mysql_config['host']}:{migrator.mysql_config['port']}")
    print(f"📍 MySQL Database: {migrator.mysql_config['database']}")
    print(f"📍 MySQL User: {migrator.mysql_config['user']}")
    
    # Confirm before proceeding
    response = input("\nProceed with migration? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Run migration
    success = migrator.run_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("1. Update your .env file with the correct MySQL credentials")
        print("2. Install the new requirements: pip install -r requirements.txt")
        print("3. Test your application with MySQL")
        print("4. Consider backing up your SQLite database before removing it")
    else:
        print("\n❌ Migration failed. Check migration.log for details.")

if __name__ == '__main__':
    main()
