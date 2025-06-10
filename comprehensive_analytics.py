"""
Comprehensive Analytics Report Generator
Creates detailed analysis of the bookstore order data for business insights
"""

from app import app, db
from model import User, Book, Order, OrderItem
from sqlalchemy import func, text
from datetime import datetime, timedelta
import csv

def generate_analytics_report():
    """Generate comprehensive analytics report"""
    
    with app.app_context():
        print("=" * 60)
        print("📊 BOOKSTORE ANALYTICS REPORT")
        print("=" * 60)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. BASIC STATISTICS
        print("1. DATABASE OVERVIEW")
        print("-" * 30)
        
        total_users = User.query.count()
        total_books = Book.query.count()
        total_orders = Order.query.count()
        total_items = OrderItem.query.count()
        
        print(f"Total Users: {total_users:,}")
        print(f"Total Books: {total_books:,}")
        print(f"Total Orders: {total_orders:,}")
        print(f"Total Order Items: {total_items:,}")
        print()
        
        # 2. REVENUE ANALYSIS
        print("2. REVENUE ANALYSIS")
        print("-" * 30)
        
        # Get all orders with valid totals
        orders_with_totals = Order.query.filter(Order.total_amount.isnot(None)).all()
        
        if orders_with_totals:
            total_revenue = sum(float(order.total_amount) for order in orders_with_totals)
            avg_order_value = total_revenue / len(orders_with_totals)
            
            print(f"Total Revenue: ${total_revenue:,.2f}")
            print(f"Orders with Revenue Data: {len(orders_with_totals):,}")
            print(f"Average Order Value: ${avg_order_value:.2f}")
            
            # Revenue distribution
            order_values = [float(order.total_amount) for order in orders_with_totals]
            order_values.sort()
            
            percentiles = [25, 50, 75, 90, 95]
            print("\\nOrder Value Distribution:")
            for p in percentiles:
                idx = int(len(order_values) * p / 100)
                if idx < len(order_values):
                    print(f"  {p}th percentile: ${order_values[idx]:.2f}")
        else:
            print("No revenue data available")
        print()
        
        # 3. ORDER STATUS ANALYSIS
        print("3. ORDER STATUS BREAKDOWN")
        print("-" * 30)
        
        status_counts = db.session.query(
            Order.status, 
            func.count(Order.order_id)
        ).group_by(Order.status).all()
        
        for status, count in status_counts:
            percentage = (count / total_orders) * 100
            print(f"{status.title()}: {count:,} ({percentage:.1f}%)")
        print()
        
        # 4. PAYMENT METHOD ANALYSIS
        print("4. PAYMENT METHOD PREFERENCES")
        print("-" * 30)
        
        payment_counts = db.session.query(
            Order.payment_method, 
            func.count(Order.order_id)
        ).group_by(Order.payment_method).all()
        
        for method, count in payment_counts:
            percentage = (count / total_orders) * 100
            print(f"{method.replace('_', ' ').title()}: {count:,} ({percentage:.1f}%)")
        print()
        
        # 5. TEMPORAL ANALYSIS
        print("5. TEMPORAL PATTERNS")
        print("-" * 30)
        
        # Orders by year
        yearly_orders = db.session.query(
            func.year(Order.order_date).label('year'),
            func.count(Order.order_id).label('count')
        ).group_by(func.year(Order.order_date)).order_by('year').all()
        
        print("Orders by Year:")
        for year, count in yearly_orders:
            print(f"  {year}: {count:,} orders")
        
        # Recent monthly trend (last 12 months)
        print("\\nLast 12 Months Trend:")
        monthly_orders = db.session.query(
            func.date_format(Order.order_date, '%Y-%m').label('month'),
            func.count(Order.order_id).label('count')
        ).filter(
            Order.order_date >= datetime.now() - timedelta(days=365)
        ).group_by(
            func.date_format(Order.order_date, '%Y-%m')
        ).order_by('month').all()
        
        for month, count in monthly_orders:
            print(f"  {month}: {count:,} orders")
        print()
        
        # 6. CUSTOMER ANALYSIS
        print("6. CUSTOMER INSIGHTS")
        print("-" * 30)
        
        # Top customers by order count
        top_customers = db.session.query(
            User.username,
            func.count(Order.order_id).label('order_count')
        ).join(Order).group_by(
            User.user_id, User.username
        ).order_by(
            func.count(Order.order_id).desc()
        ).limit(10).all()
        
        print("Top 10 Customers by Order Count:")
        for i, (username, order_count) in enumerate(top_customers, 1):
            print(f"  {i:2d}. {username}: {order_count} orders")
        
        # Customer activity distribution
        customer_orders = db.session.query(
            func.count(Order.order_id).label('order_count')
        ).group_by(Order.user_id).all()
        
        order_counts = [count[0] for count in customer_orders]
        
        print(f"\\nCustomer Activity Distribution:")
        print(f"  One-time customers: {order_counts.count(1)} ({(order_counts.count(1)/len(order_counts)*100):.1f}%)")
        repeat_customers = len([c for c in order_counts if c > 1])
        print(f"  Repeat customers: {repeat_customers} ({(repeat_customers/len(order_counts)*100):.1f}%)")
        
        if order_counts:
            avg_orders_per_customer = sum(order_counts) / len(order_counts)
            print(f"  Average orders per customer: {avg_orders_per_customer:.1f}")
        print()
        
        # 7. PRODUCT ANALYSIS
        print("7. PRODUCT PERFORMANCE")
        print("-" * 30)
        
        # Top selling books
        top_books = db.session.query(
            Book.title,
            Book.author,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).group_by(
            Book.book_id, Book.title, Book.author
        ).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        print("Top 10 Best-Selling Books:")
        for i, (title, author, total_sold) in enumerate(top_books, 1):
            print(f"  {i:2d}. {title} by {author}: {total_sold} copies")
        
        # Genre popularity
        genre_sales = db.session.query(
            Book.genre,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).group_by(Book.genre).order_by(
            func.sum(OrderItem.quantity).desc()
        ).all()
        
        print("\\nGenre Popularity by Units Sold:")
        for genre, total_sold in genre_sales:
            print(f"  {genre}: {total_sold} copies")
        print()
        
        # 8. ORDER SIZE ANALYSIS
        print("8. ORDER SIZE PATTERNS")
        print("-" * 30)
        
        order_sizes = db.session.query(
            func.count(OrderItem.order_item_id).label('items_per_order')
        ).group_by(OrderItem.order_id).all()
        
        size_counts = {}
        for size in order_sizes:
            items = size[0]
            size_counts[items] = size_counts.get(items, 0) + 1
        
        print("Items per Order Distribution:")
        for items in sorted(size_counts.keys()):
            count = size_counts[items]
            percentage = (count / len(order_sizes)) * 100
            print(f"  {items} item{'s' if items != 1 else ''}: {count:,} orders ({percentage:.1f}%)")
        print()
        
        # 9. SEASONAL ANALYSIS
        print("9. SEASONAL TRENDS")
        print("-" * 30)
        
        monthly_distribution = db.session.query(
            func.month(Order.order_date).label('month'),
            func.count(Order.order_id).label('count')
        ).group_by(func.month(Order.order_date)).order_by('month').all()
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        print("Orders by Month (All Years):")
        for month_num, count in monthly_distribution:
            month_name = month_names[month_num] if month_num <= 12 else f"Month {month_num}"
            print(f"  {month_name}: {count:,} orders")
        print()
        
        # 10. BUSINESS INSIGHTS
        print("10. KEY BUSINESS INSIGHTS")
        print("-" * 30)
        
        insights = []
        
        # Calculate repeat customer rate
        if order_counts:
            repeat_rate = (repeat_customers / len(order_counts)) * 100
            insights.append(f"• Customer Retention: {repeat_rate:.1f}% of customers are repeat buyers")
        
        # Identify peak months
        if monthly_distribution:
            peak_month = max(monthly_distribution, key=lambda x: x[1])
            peak_month_name = month_names[peak_month[0]] if peak_month[0] <= 12 else f"Month {peak_month[0]}"
            insights.append(f"• Peak Sales Month: {peak_month_name} with {peak_month[1]:,} orders")
        
        # Order completion rate
        completed_orders = sum(count for status, count in status_counts if status in ['completed', 'delivered'])
        completion_rate = (completed_orders / total_orders) * 100
        insights.append(f"• Order Completion Rate: {completion_rate:.1f}% of orders are completed/delivered")
        
        # Average items per order
        if order_sizes:
            avg_items = sum(size[0] for size in order_sizes) / len(order_sizes)
            insights.append(f"• Average Items per Order: {avg_items:.1f}")
        
        for insight in insights:
            print(insight)
        
        print()
        print("=" * 60)
        print("📈 END OF ANALYTICS REPORT")
        print("=" * 60)

if __name__ == '__main__':
    generate_analytics_report()
