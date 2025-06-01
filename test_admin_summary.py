#!/usr/bin/env python3
"""
Test script to verify admin summary data and functionality
"""

import sys
import os
sys.path.append('.')

from model import db, User, Book, Order, OrderItem
from app import app

def test_admin_summary_data():
    """Test the admin summary data retrieval"""
    with app.app_context():
        print("🔍 Testing Admin Summary Data")
        print("=" * 50)
        
        # Book Statistics
        total_books = Book.query.count()
        total_stock = db.session.query(db.func.sum(Book.stock)).scalar() or 0
        print(f"📚 Total Books: {total_books}")
        print(f"📦 Total Stock: {total_stock}")
        
        # Books by genre
        genre_stats = db.session.query(
            Book.genre, 
            db.func.count(Book.book_id).label('count'),
            db.func.sum(Book.stock).label('total_stock')
        ).group_by(Book.genre).all()
        
        print(f"\n📊 Books by Genre:")
        for genre, count, stock in genre_stats[:5]:  # Show top 5
            print(f"  • {genre or 'Unclassified'}: {count} books ({stock} stock)")
        
        # Low stock books (less than 10)
        low_stock_books = Book.query.filter(Book.stock < 10).order_by(Book.stock.asc()).all()
        print(f"\n⚠️  Low Stock Books: {len(low_stock_books)}")
        for book in low_stock_books[:5]:  # Show top 5
            print(f"  • {book.title}: {book.stock} left")
        
        # Order Statistics
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        print(f"\n🛒 Total Orders: {total_orders}")
        print(f"💰 Total Revenue: ${total_revenue:.2f}")
        
        # Orders by status
        order_status_stats = db.session.query(
            Order.status,
            db.func.count(Order.order_id).label('count'),
            db.func.sum(Order.total_amount).label('total_amount')
        ).group_by(Order.status).all()
        
        print(f"\n📈 Orders by Status:")
        for status, count, revenue in order_status_stats:
            print(f"  • {status.title()}: {count} orders (${revenue:.2f})")
        
        # Top selling books
        top_books = db.session.query(
            Book.title,
            Book.author,
            Book.price,
            db.func.count(OrderItem.order_item_id).label('times_ordered'),
            db.func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem, Book.book_id == OrderItem.book_id)\
         .group_by(Book.book_id)\
         .order_by(db.func.sum(OrderItem.quantity).desc())\
         .limit(5).all()
        
        print(f"\n🏆 Top 5 Selling Books:")
        for book in top_books:
            print(f"  • {book.title} by {book.author}: {book.total_sold} sold")
        
        # Customer statistics
        total_customers = User.query.count()
        customers_with_orders = db.session.query(db.func.count(db.func.distinct(Order.user_id))).scalar() or 0
        print(f"\n👥 Total Customers: {total_customers}")
        print(f"🛍️  Active Customers: {customers_with_orders}")
        
        print("\n✅ Admin Summary Test Completed!")
        print(f"📊 Data Summary: {total_books} books, {total_orders} orders, ${total_revenue:.2f} revenue")

if __name__ == "__main__":
    test_admin_summary_data()
