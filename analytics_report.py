"""
Comprehensive Analytics Report Generator
Analyzes the bookstore order data for business insights
"""

from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
import calendar
from app import app, db
from model import User, Book, Order, OrderItem
from sqlalchemy import func, extract, desc, and_

class BookstoreAnalytics:
    
    def __init__(self):
        self.report = []
    
    def log(self, message):
        """Add message to report"""
        print(message)
        self.report.append(message)
    
    def generate_executive_summary(self):
        """Generate high-level business metrics"""
        self.log("📊 EXECUTIVE SUMMARY")
        self.log("=" * 60)
        
        with app.app_context():
            # Basic metrics
            total_orders = Order.query.count()
            total_users = User.query.count()
            total_books = Book.query.count()
            active_customers = db.session.query(func.count(func.distinct(Order.user_id))).scalar()
            
            # Revenue metrics
            total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or Decimal('0')
            avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0')
            
            # Item metrics
            total_items_sold = db.session.query(func.sum(OrderItem.quantity)).scalar() or 0
            avg_items_per_order = total_items_sold / total_orders if total_orders > 0 else 0
            
            self.log(f"📈 Total Orders: {total_orders:,}")
            self.log(f"👥 Total Customers: {total_users}")
            self.log(f"🛍️ Active Customers: {active_customers} ({(active_customers/total_users)*100:.1f}%)")
            self.log(f"📚 Books in Catalog: {total_books}")
            self.log(f"📦 Total Items Sold: {total_items_sold:,}")
            self.log(f"💰 Total Revenue: ${float(total_revenue):,.2f}")
            self.log(f"📊 Average Order Value: ${float(avg_order_value):,.2f}")
            self.log(f"📖 Avg Items per Order: {avg_items_per_order:.1f}")
    
    def analyze_monthly_trends(self):
        """Analyze monthly sales trends"""
        self.log(f"\n📅 MONTHLY SALES TRENDS")
        self.log("=" * 60)
        
        with app.app_context():
            monthly_stats = db.session.query(
                extract('year', Order.order_date).label('year'),
                extract('month', Order.order_date).label('month'),
                func.count(Order.order_id).label('orders'),
                func.sum(Order.total_amount).label('revenue'),
                func.sum(OrderItem.quantity).label('items_sold')
            ).join(OrderItem).group_by('year', 'month').order_by('year', 'month').all()
            
            self.log(f"{'Month':<15} {'Orders':<8} {'Revenue':<12} {'Items':<8} {'AOV':<8}")
            self.log("-" * 60)
            
            for stat in monthly_stats[-12:]:  # Last 12 months
                month_name = calendar.month_name[int(stat.month)]
                year = int(stat.year)
                revenue = float(stat.revenue) if stat.revenue else 0
                aov = revenue / stat.orders if stat.orders > 0 else 0
                
                self.log(f"{month_name} {year:<6} {stat.orders:<8} ${revenue:<11,.0f} {stat.items_sold:<8} ${aov:<7.0f}")
    
    def analyze_customer_segments(self):
        """Analyze customer behavior segments"""
        self.log(f"\n👥 CUSTOMER ANALYSIS")
        self.log("=" * 60)
        
        with app.app_context():
            # Top customers by orders
            top_customers_orders = db.session.query(
                User.username,
                func.count(Order.order_id).label('order_count'),
                func.sum(Order.total_amount).label('total_spent'),
                func.avg(Order.total_amount).label('avg_order_value')
            ).join(Order).group_by(User.user_id, User.username).order_by(desc('order_count')).limit(10).all()
            
            self.log(f"🏆 TOP 10 CUSTOMERS BY ORDER COUNT:")
            self.log(f"{'Customer':<15} {'Orders':<8} {'Total Spent':<12} {'Avg Order':<10}")
            self.log("-" * 50)
            
            for customer in top_customers_orders:
                spent = float(customer.total_spent) if customer.total_spent else 0
                avg_order = float(customer.avg_order_value) if customer.avg_order_value else 0
                self.log(f"{customer.username:<15} {customer.order_count:<8} ${spent:<11,.0f} ${avg_order:<9.0f}")
            
            # Customer segmentation by order frequency
            customer_segments = db.session.query(
                func.count(Order.order_id).label('order_count'),
                func.count(func.distinct(Order.user_id)).label('customer_count')
            ).group_by(Order.user_id).subquery()
            
            # Segment distribution
            segments = {
                'One-time buyers': db.session.query(func.count(Order.user_id)).filter(
                    Order.user_id.in_(
                        db.session.query(Order.user_id).group_by(Order.user_id).having(func.count(Order.order_id) == 1)
                    )
                ).scalar(),
                'Repeat customers (2-5 orders)': db.session.query(func.count(func.distinct(Order.user_id))).filter(
                    Order.user_id.in_(
                        db.session.query(Order.user_id).group_by(Order.user_id).having(
                            and_(func.count(Order.order_id) >= 2, func.count(Order.order_id) <= 5)
                        )
                    )
                ).scalar(),
                'Loyal customers (6+ orders)': db.session.query(func.count(func.distinct(Order.user_id))).filter(
                    Order.user_id.in_(
                        db.session.query(Order.user_id).group_by(Order.user_id).having(func.count(Order.order_id) >= 6)
                    )
                ).scalar()
            }
            
            self.log(f"\n📊 CUSTOMER SEGMENTS:")
            total_active = sum(segments.values())
            for segment, count in segments.items():
                percentage = (count / total_active) * 100 if total_active > 0 else 0
                self.log(f"   {segment}: {count} customers ({percentage:.1f}%)")
    
    def analyze_product_performance(self):
        """Analyze book and genre performance"""
        self.log(f"\n📚 PRODUCT PERFORMANCE")
        self.log("=" * 60)
        
        with app.app_context():
            # Top selling books
            top_books = db.session.query(
                Book.title,
                Book.author,
                Book.genre,
                func.sum(OrderItem.quantity).label('copies_sold'),
                func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue')
            ).join(OrderItem).group_by(Book.book_id, Book.title, Book.author, Book.genre).order_by(desc('copies_sold')).limit(10).all()
            
            self.log(f"📖 TOP 10 BEST-SELLING BOOKS:")
            self.log(f"{'Title':<25} {'Author':<15} {'Genre':<12} {'Sold':<6} {'Revenue':<10}")
            self.log("-" * 75)
            
            for book in top_books:
                title = (book.title[:22] + '...') if len(book.title) > 25 else book.title
                author = (book.author[:12] + '...') if len(book.author) > 15 else book.author
                genre = book.genre or 'N/A'
                revenue = float(book.revenue) if book.revenue else 0
                self.log(f"{title:<25} {author:<15} {genre:<12} {book.copies_sold:<6} ${revenue:<9,.0f}")
            
            # Genre performance
            genre_stats = db.session.query(
                Book.genre,
                func.count(func.distinct(Book.book_id)).label('book_count'),
                func.sum(OrderItem.quantity).label('copies_sold'),
                func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue')
            ).join(OrderItem).group_by(Book.genre).order_by(desc('revenue')).all()
            
            self.log(f"\n🎭 GENRE PERFORMANCE:")
            self.log(f"{'Genre':<20} {'Books':<6} {'Sold':<8} {'Revenue':<12} {'Avg/Book':<10}")
            self.log("-" * 65)
            
            for genre in genre_stats:
                genre_name = genre.genre or 'Unclassified'
                revenue = float(genre.revenue) if genre.revenue else 0
                avg_per_book = revenue / genre.book_count if genre.book_count > 0 else 0
                self.log(f"{genre_name:<20} {genre.book_count:<6} {genre.copies_sold:<8} ${revenue:<11,.0f} ${avg_per_book:<9,.0f}")
    
    def analyze_order_patterns(self):
        """Analyze order status, payment methods, and delivery patterns"""
        self.log(f"\n📦 ORDER PATTERNS")
        self.log("=" * 60)
        
        with app.app_context():
            # Order status distribution
            status_stats = db.session.query(
                Order.status,
                func.count(Order.order_id).label('count'),
                func.sum(Order.total_amount).label('revenue')
            ).group_by(Order.status).order_by(desc('count')).all()
            
            self.log(f"📋 ORDER STATUS DISTRIBUTION:")
            total_orders = sum(stat.count for stat in status_stats)
            for stat in status_stats:
                percentage = (stat.count / total_orders) * 100
                revenue = float(stat.revenue) if stat.revenue else 0
                self.log(f"   {stat.status.title()}: {stat.count} orders ({percentage:.1f}%) - ${revenue:,.0f}")
            
            # Payment method preferences
            payment_stats = db.session.query(
                Order.payment_method,
                func.count(Order.order_id).label('count'),
                func.avg(Order.total_amount).label('avg_order_value')
            ).group_by(Order.payment_method).order_by(desc('count')).all()
            
            self.log(f"\n💳 PAYMENT METHOD PREFERENCES:")
            for stat in payment_stats:
                percentage = (stat.count / total_orders) * 100
                avg_value = float(stat.avg_order_value) if stat.avg_order_value else 0
                method = stat.payment_method.replace('_', ' ').title()
                self.log(f"   {method}: {stat.count} orders ({percentage:.1f}%) - Avg: ${avg_value:.0f}")
            
            # Delivery charge analysis
            delivery_stats = db.session.query(
                func.count(Order.order_id).label('total_orders'),
                func.sum(func.case([(Order.delivery_charge == 0, 1)], else_=0)).label('free_shipping'),
                func.avg(Order.delivery_charge).label('avg_delivery_charge')
            ).scalar()
            
            free_shipping_orders = db.session.query(func.count(Order.order_id)).filter(Order.delivery_charge == 0).scalar()
            free_shipping_percentage = (free_shipping_orders / total_orders) * 100
            
            self.log(f"\n🚚 DELIVERY PATTERNS:")
            self.log(f"   Free Shipping Orders: {free_shipping_orders} ({free_shipping_percentage:.1f}%)")
            self.log(f"   Paid Shipping Orders: {total_orders - free_shipping_orders} ({100 - free_shipping_percentage:.1f}%)")
    
    def generate_business_insights(self):
        """Generate actionable business insights"""
        self.log(f"\n💡 BUSINESS INSIGHTS & RECOMMENDATIONS")
        self.log("=" * 60)
        
        with app.app_context():
            # Calculate key metrics for insights
            total_orders = Order.query.count()
            total_revenue = float(db.session.query(func.sum(Order.total_amount)).scalar() or 0)
            
            # Completion rate
            completed_orders = Order.query.filter(Order.status.in_(['completed', 'delivered'])).count()
            completion_rate = (completed_orders / total_orders) * 100
            
            # Free shipping threshold effectiveness
            free_shipping_orders = Order.query.filter(Order.delivery_charge == 0).count()
            free_shipping_rate = (free_shipping_orders / total_orders) * 100
            
            # Average order frequency per customer
            active_customers = db.session.query(func.count(func.distinct(Order.user_id))).scalar()
            avg_orders_per_customer = total_orders / active_customers if active_customers > 0 else 0
            
            self.log(f"🎯 KEY PERFORMANCE INDICATORS:")
            self.log(f"   Order Completion Rate: {completion_rate:.1f}%")
            self.log(f"   Free Shipping Rate: {free_shipping_rate:.1f}%")
            self.log(f"   Customer Retention: {avg_orders_per_customer:.1f} orders per customer")
            
            self.log(f"\n📈 RECOMMENDATIONS:")
            
            if completion_rate < 90:
                self.log(f"   • Improve order fulfillment process (current completion: {completion_rate:.1f}%)")
            
            if free_shipping_rate < 40:
                self.log(f"   • Consider lowering free shipping threshold to increase AOV")
            
            if avg_orders_per_customer < 3:
                self.log(f"   • Implement customer retention programs (current avg: {avg_orders_per_customer:.1f})")
            
            self.log(f"   • Focus marketing on top-performing genres")
            self.log(f"   • Develop loyalty program for repeat customers")
            self.log(f"   • Optimize inventory based on seasonal trends")
    
    def generate_full_report(self):
        """Generate complete analytics report"""
        self.log(f"📊 BOOKSTORE ANALYTICS REPORT")
        self.log(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        self.log("=" * 80)
        
        self.generate_executive_summary()
        self.analyze_monthly_trends()
        self.analyze_customer_segments()
        self.analyze_product_performance()
        self.analyze_order_patterns()
        self.generate_business_insights()
        
        self.log(f"\n" + "=" * 80)
        self.log(f"📊 END OF ANALYTICS REPORT")
        self.log(f"Total database records analyzed: {Order.query.count() if app.app_context().__enter__() else 'N/A'} orders")

def main():
    analytics = BookstoreAnalytics()
    analytics.generate_full_report()

if __name__ == "__main__":
    main()
