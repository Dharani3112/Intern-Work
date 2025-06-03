#!/usr/bin/env python3
"""
Database Verification Script
Checks if 100 books and order histories are present in the bookstore database
"""

from app import app
from model import db, User, Book, Order, OrderItem, Review, BookImage
from sqlalchemy import func
from datetime import datetime, timedelta

def check_database_contents():
    """Check and display database statistics"""
    
    with app.app_context():
        print("🔍 BOOKSTORE DATABASE VERIFICATION")
        print("=" * 50)
        
        # Check Books
        book_count = Book.query.count()
        print(f"📚 BOOKS: {book_count}")
        
        if book_count >= 100:
            print("✅ Target of 100 books: ACHIEVED")
        else:
            print(f"❌ Target of 100 books: MISSING ({100 - book_count} books needed)")
        
        # Show book genres distribution
        genre_stats = db.session.query(
            Book.genre, 
            func.count(Book.book_id).label('count')
        ).group_by(Book.genre).order_by(func.count(Book.book_id).desc()).all()
        
        print(f"\n📊 Books by Genre ({len(genre_stats)} genres):")
        for genre, count in genre_stats:
            print(f"   • {genre}: {count} books")
        
        # Check Users
        user_count = User.query.count()
        print(f"\n👥 USERS: {user_count}")
        
        # Check Orders
        order_count = Order.query.count()
        print(f"\n🛒 ORDERS: {order_count}")
        
        if order_count > 0:
            print("✅ Order history: PRESENT")
            
            # Order status distribution
            status_stats = db.session.query(
                Order.status,
                func.count(Order.order_id).label('count')
            ).group_by(Order.status).all()
            
            print(f"\n📈 Order Status Distribution:")
            total_orders = sum(count for _, count in status_stats)
            for status, count in status_stats:
                percentage = (count / total_orders * 100) if total_orders > 0 else 0
                print(f"   • {status.title()}: {count} orders ({percentage:.1f}%)")
            
            # Check Order Items
            order_item_count = OrderItem.query.count()
            print(f"\n📦 ORDER ITEMS: {order_item_count}")
            
            # Revenue calculation
            total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
            avg_order_value = db.session.query(func.avg(Order.total_amount)).scalar() or 0
            
            print(f"\n💰 REVENUE STATISTICS:")
            print(f"   • Total Revenue: ${total_revenue:,.2f}")
            print(f"   • Average Order Value: ${avg_order_value:.2f}")
            
            # Date range of orders
            earliest_order = db.session.query(func.min(Order.order_date)).scalar()
            latest_order = db.session.query(func.max(Order.order_date)).scalar()
            
            if earliest_order and latest_order:
                print(f"\n📅 ORDER DATE RANGE:")
                print(f"   • Earliest: {earliest_order.strftime('%Y-%m-%d')}")
                print(f"   • Latest: {latest_order.strftime('%Y-%m-%d')}")
                days_span = (latest_order - earliest_order).days
                print(f"   • Span: {days_span} days")
        else:
            print("❌ Order history: MISSING")
        
        # Check Reviews
        review_count = Review.query.count()
        print(f"\n⭐ REVIEWS: {review_count}")
        
        # Check Book Images
        image_count = BookImage.query.count()
        print(f"\n🖼️ BOOK IMAGES: {image_count}")
        
        # Most popular books (by order frequency)
        print(f"\n🏆 TOP 10 MOST ORDERED BOOKS:")
        popular_books = db.session.query(
            Book.title,
            Book.author,
            func.count(OrderItem.order_item_id).label('order_count')
        ).join(OrderItem, Book.book_id == OrderItem.book_id)\
         .group_by(Book.book_id, Book.title, Book.author)\
         .order_by(func.count(OrderItem.order_item_id).desc())\
         .limit(10).all()
        
        for i, (title, author, count) in enumerate(popular_books, 1):
            print(f"   {i:2d}. '{title}' by {author} - {count} orders")
        
        # Recent orders (last 10)
        print(f"\n🕐 RECENT ORDERS (Last 10):")
        recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
        
        for order in recent_orders:
            user = User.query.get(order.user_id)
            username = user.username if user else "Unknown"
            print(f"   • Order #{order.order_id} - {username} - ${order.total_amount:.2f} - {order.status} - {order.order_date.strftime('%Y-%m-%d %H:%M')}")
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY:")
        print(f"   Books: {book_count}/100 {'✅' if book_count >= 100 else '❌'}")
        print(f"   Orders: {order_count} {'✅' if order_count > 0 else '❌'}")
        print(f"   Users: {user_count}")
        print(f"   Revenue: ${total_revenue:,.2f}")
        
        if book_count >= 100 and order_count > 0:
            print("\n🎉 DATABASE VERIFICATION: SUCCESS!")
            print("✅ Your bookstore database is fully populated and ready!")
        else:
            print("\n⚠️  DATABASE VERIFICATION: INCOMPLETE")
            if book_count < 100:
                print(f"❌ Need to add {100 - book_count} more books")
            if order_count == 0:
                print("❌ Need to generate order history")

if __name__ == '__main__':
    check_database_contents()
