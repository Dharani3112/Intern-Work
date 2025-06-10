#!/usr/bin/env python3
"""
Database to CSV Export Script
Exports all database tables to CSV files for backup or analysis
"""

import os
import csv
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from model import db, User, Book, BookImage, Review, CartItem, Order, OrderItem

def create_export_directory():
    """Create exports directory if it doesn't exist"""
    export_dir = os.path.join(os.path.dirname(__file__), 'database_exports')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    return export_dir

def export_books_to_csv(export_dir):
    """Export all books to CSV"""
    filename = os.path.join(export_dir, 'books.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'book_id', 'title', 'author', 'isbn', 'publisher', 'publication_year',
            'pages', 'language', 'description', 'price', 'delivery_date', 
            'genre', 'format', 'rating_avg', 'stock'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        books = Book.query.all()
        for book in books:
            writer.writerow({
                'book_id': book.book_id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'publisher': book.publisher,
                'publication_year': book.publication_year,
                'pages': book.pages,
                'language': book.language,
                'description': book.description,
                'price': float(book.price) if book.price else None,
                'delivery_date': book.delivery_date,
                'genre': book.genre,
                'format': book.format,
                'rating_avg': book.rating_avg,
                'stock': book.stock
            })
    
    print(f"✅ Exported {len(books)} books to {filename}")
    return len(books)

def export_users_to_csv(export_dir):
    """Export all users to CSV (excluding sensitive password data)"""
    filename = os.path.join(export_dir, 'users.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'user_id', 'username', 'email', 'first_name', 'last_name', 'mobile_number'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        users = User.query.all()
        for user in users:
            writer.writerow({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mobile_number': user.mobile_number
            })
    
    print(f"✅ Exported {len(users)} users to {filename}")
    return len(users)

def export_orders_to_csv(export_dir):
    """Export all orders to CSV"""
    filename = os.path.join(export_dir, 'orders.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'order_id', 'user_id', 'username', 'order_date', 'status', 
            'total_amount', 'shipping_address', 'payment_method'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        orders = Order.query.all()
        for order in orders:
            user = User.query.get(order.user_id)
            writer.writerow({
                'order_id': order.order_id,
                'user_id': order.user_id,
                'username': user.username if user else 'Unknown',
                'order_date': order.order_date.isoformat() if order.order_date else None,
                'status': order.status,
                'total_amount': float(order.total_amount) if order.total_amount else None,
                'shipping_address': order.shipping_address,
                'payment_method': order.payment_method
            })
    
    print(f"✅ Exported {len(orders)} orders to {filename}")
    return len(orders)

def export_order_items_to_csv(export_dir):
    """Export all order items to CSV"""
    filename = os.path.join(export_dir, 'order_items.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'order_item_id', 'order_id', 'book_id', 'book_title', 'book_author',
            'quantity', 'price_at_time', 'total_price'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        order_items = OrderItem.query.all()
        for item in order_items:
            book = Book.query.get(item.book_id)
            writer.writerow({
                'order_item_id': item.order_item_id,
                'order_id': item.order_id,
                'book_id': item.book_id,
                'book_title': book.title if book else 'Unknown',
                'book_author': book.author if book else 'Unknown',
                'quantity': item.quantity,
                'price_at_time': float(item.price_at_time) if item.price_at_time else None,
                'total_price': float(item.quantity * item.price_at_time) if item.price_at_time else None
            })
    
    print(f"✅ Exported {len(order_items)} order items to {filename}")
    return len(order_items)

def export_reviews_to_csv(export_dir):
    """Export all reviews to CSV"""
    filename = os.path.join(export_dir, 'reviews.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'review_id', 'user_id', 'username', 'book_id', 'book_title',
            'rating', 'description', 'created_at'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        reviews = Review.query.all()
        for review in reviews:
            user = User.query.get(review.user_id)
            book = Book.query.get(review.book_id)
            writer.writerow({
                'review_id': review.review_id,
                'user_id': review.user_id,
                'username': user.username if user else 'Unknown',
                'book_id': review.book_id,
                'book_title': book.title if book else 'Unknown',
                'rating': review.rating,
                'description': review.description,
                'created_at': review.created_at.isoformat() if review.created_at else None
            })
    
    print(f"✅ Exported {len(reviews)} reviews to {filename}")
    return len(reviews)

def export_book_images_to_csv(export_dir):
    """Export all book images to CSV"""
    filename = os.path.join(export_dir, 'book_images.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'image_id', 'book_id', 'book_title', 'image_url', 'is_main'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        images = BookImage.query.all()
        for image in images:
            book = Book.query.get(image.book_id)
            writer.writerow({
                'image_id': image.image_id,
                'book_id': image.book_id,
                'book_title': book.title if book else 'Unknown',
                'image_url': image.image_url,
                'is_main': image.is_main
            })
    
    print(f"✅ Exported {len(images)} book images to {filename}")
    return len(images)

def export_cart_items_to_csv(export_dir):
    """Export current cart items to CSV"""
    filename = os.path.join(export_dir, 'cart_items.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'cart_item_id', 'user_id', 'username', 'book_id', 'book_title',
            'quantity', 'added_at'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        cart_items = CartItem.query.all()
        for item in cart_items:
            user = User.query.get(item.user_id)
            book = Book.query.get(item.book_id)
            writer.writerow({
                'cart_item_id': item.cart_item_id,
                'user_id': item.user_id,
                'username': user.username if user else 'Unknown',
                'book_id': item.book_id,
                'book_title': book.title if book else 'Unknown',
                'quantity': item.quantity,
                'added_at': item.added_at.isoformat() if hasattr(item, 'added_at') and item.added_at else None
            })
    
    print(f"✅ Exported {len(cart_items)} cart items to {filename}")
    return len(cart_items)

def create_summary_csv(export_dir, stats):
    """Create a summary CSV with export statistics"""
    filename = os.path.join(export_dir, 'export_summary.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['table_name', 'record_count', 'export_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        export_date = datetime.now().isoformat()
        
        for table_name, count in stats.items():
            writer.writerow({
                'table_name': table_name,
                'record_count': count,
                'export_date': export_date
            })
    
    print(f"✅ Created export summary at {filename}")

def main():
    """Main export function"""
    print("🔄 Starting Database Export to CSV...")
    print("=" * 50)
    
    with app.app_context():
        # Create export directory
        export_dir = create_export_directory()
        print(f"📁 Export directory: {export_dir}")
        print()
        
        # Track statistics
        stats = {}
        
        # Export each table
        try:
            stats['books'] = export_books_to_csv(export_dir)
            stats['users'] = export_users_to_csv(export_dir)
            stats['orders'] = export_orders_to_csv(export_dir)
            stats['order_items'] = export_order_items_to_csv(export_dir)
            stats['reviews'] = export_reviews_to_csv(export_dir)
            stats['book_images'] = export_book_images_to_csv(export_dir)
            stats['cart_items'] = export_cart_items_to_csv(export_dir)
            
            # Create summary
            create_summary_csv(export_dir, stats)
            
            print()
            print("=" * 50)
            print("🎉 DATABASE EXPORT COMPLETED SUCCESSFULLY!")
            print(f"📊 Export Statistics:")
            total_records = 0
            for table, count in stats.items():
                print(f"   • {table.title().replace('_', ' ')}: {count:,} records")
                total_records += count
            
            print(f"\n📈 Total Records Exported: {total_records:,}")
            print(f"📁 Files saved to: {export_dir}")
            print("\n💡 You can now:")
            print("   - Open CSV files in Excel or Google Sheets")
            print("   - Import into other databases")
            print("   - Perform data analysis")
            print("   - Create backups")
            
        except Exception as e:
            print(f"❌ Error during export: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
