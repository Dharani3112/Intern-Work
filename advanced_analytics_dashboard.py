"""
Advanced Analytics Dashboard for Bookstore Data
Comprehensive business intelligence and data analysis
"""

from app import app, db
from model import User, Book, Order, OrderItem
from sqlalchemy import func, extract, text
from datetime import datetime, timedelta
import json
from decimal import Decimal

class BookstoreAnalytics:
    def __init__(self):
        self.app = app
        self.db = db
    
    def generate_executive_summary(self):
        """Generate executive summary for business stakeholders"""
        print("🎯 EXECUTIVE BUSINESS SUMMARY")
        print("=" * 60)
        
        with self.app.app_context():
            # Key Performance Indicators
            total_orders = Order.query.count()
            total_revenue = self.db.session.query(func.sum(Order.total_amount)).scalar() or Decimal('0')
            total_customers = User.query.count()
            total_books = Book.query.count()
            
            # Active customers (placed orders in last 6 months)
            six_months_ago = datetime.now() - timedelta(days=180)
            active_customers = self.db.session.query(func.count(func.distinct(Order.user_id))).filter(
                Order.order_date >= six_months_ago
            ).scalar()
            
            # Average metrics
            avg_order_value = float(total_revenue) / total_orders if total_orders > 0 else 0
            orders_per_customer = total_orders / total_customers if total_customers > 0 else 0
            
            print(f"📊 KEY BUSINESS METRICS")
            print(f"   Total Revenue: ${float(total_revenue):,.2f}")
            print(f"   Total Orders: {total_orders:,}")
            print(f"   Active Customers: {active_customers}/{total_customers}")
            print(f"   Product Catalog: {total_books} books")
            print(f"   Average Order Value: ${avg_order_value:.2f}")
            print(f"   Orders per Customer: {orders_per_customer:.1f}")
            print()
            
            # Revenue growth analysis
            print(f"📈 GROWTH ANALYSIS")
            monthly_revenue = self.db.session.query(
                extract('year', Order.order_date).label('year'),
                extract('month', Order.order_date).label('month'),
                func.sum(Order.total_amount).label('revenue')
            ).group_by('year', 'month').order_by('year', 'month').all()
            
            if len(monthly_revenue) >= 2:
                recent_month = float(monthly_revenue[-1].revenue) if monthly_revenue[-1].revenue else 0
                previous_month = float(monthly_revenue[-2].revenue) if monthly_revenue[-2].revenue else 0
                
                if previous_month > 0:
                    growth_rate = ((recent_month - previous_month) / previous_month) * 100
                    print(f"   Month-over-Month Growth: {growth_rate:+.1f}%")
                
                # Year-over-year if available
                if len(monthly_revenue) >= 12:
                    current_month_last_year = float(monthly_revenue[-13].revenue) if len(monthly_revenue) > 12 and monthly_revenue[-13].revenue else 0
                    if current_month_last_year > 0:
                        yoy_growth = ((recent_month - current_month_last_year) / current_month_last_year) * 100
                        print(f"   Year-over-Year Growth: {yoy_growth:+.1f}%")
            
            # Customer segmentation
            print(f"\\n👥 CUSTOMER INSIGHTS")
            
            # High-value customers (top 20% by spending)
            customer_spending = self.db.session.query(
                Order.user_id,
                func.sum(Order.total_amount).label('total_spent'),
                func.count(Order.order_id).label('order_count')
            ).group_by(Order.user_id).all()
            
            if customer_spending:
                customer_values = [float(c.total_spent) for c in customer_spending]
                customer_values.sort(reverse=True)
                
                # Top 20% threshold
                top_20_threshold = customer_values[int(len(customer_values) * 0.2)]
                high_value_customers = len([v for v in customer_values if v >= top_20_threshold])
                high_value_revenue = sum([v for v in customer_values if v >= top_20_threshold])
                
                print(f"   High-Value Customers (Top 20%): {high_value_customers}")
                print(f"   Revenue from Top 20%: ${high_value_revenue:,.2f} ({(high_value_revenue/float(total_revenue)*100):.1f}%)")
                print(f"   Average High-Value Customer: ${high_value_revenue/high_value_customers:.2f}")

    def analyze_seasonal_trends(self):
        """Analyze seasonal purchasing patterns"""
        print("\\n🌟 SEASONAL TREND ANALYSIS")
        print("=" * 60)
        
        with self.app.app_context():
            # Monthly sales pattern
            monthly_data = self.db.session.query(
                extract('month', Order.order_date).label('month'),
                func.count(Order.order_id).label('orders'),
                func.sum(Order.total_amount).label('revenue'),
                func.avg(Order.total_amount).label('avg_order')
            ).group_by('month').order_by('month').all()
            
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            print("📅 MONTHLY PERFORMANCE PATTERNS")
            print("Month    Orders    Revenue      Avg Order")
            print("-" * 45)
            
            for month_data in monthly_data:
                month_name = months[int(month_data.month) - 1]
                orders = month_data.orders
                revenue = float(month_data.revenue) if month_data.revenue else 0
                avg_order = float(month_data.avg_order) if month_data.avg_order else 0
                
                print(f"{month_name:<8} {orders:<8} ${revenue:<10,.0f} ${avg_order:.2f}")
            
            # Identify peak seasons
            revenues = [float(m.revenue) if m.revenue else 0 for m in monthly_data]
            if revenues:
                max_revenue = max(revenues)
                peak_month_idx = revenues.index(max_revenue)
                peak_month = months[peak_month_idx]
                
                min_revenue = min(revenues)
                slow_month_idx = revenues.index(min_revenue)
                slow_month = months[slow_month_idx]
                
                print(f"\\n🔥 Peak Season: {peak_month} (${max_revenue:,.0f})")
                print(f"📉 Slowest Month: {slow_month} (${min_revenue:,.0f})")
                print(f"📊 Seasonal Variation: {((max_revenue - min_revenue) / min_revenue * 100):.1f}%")

    def analyze_product_performance(self):
        """Analyze book and genre performance"""
        print("\\n📚 PRODUCT PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        with self.app.app_context():
            # Top-selling books
            print("🏆 TOP 10 BEST-SELLING BOOKS")
            top_books = self.db.session.query(
                Book.title,
                Book.author,
                Book.genre,
                func.sum(OrderItem.quantity).label('copies_sold'),
                func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue')
            ).join(OrderItem).group_by(Book.book_id, Book.title, Book.author, Book.genre).order_by(
                func.sum(OrderItem.quantity).desc()
            ).limit(10).all()
            
            print("Rank  Title                           Author              Copies   Revenue")
            print("-" * 80)
            for i, book in enumerate(top_books, 1):
                title = book.title[:25] + "..." if len(book.title) > 25 else book.title
                author = book.author[:15] + "..." if len(book.author) > 15 else book.author
                revenue = float(book.revenue) if book.revenue else 0
                print(f"{i:<4}  {title:<30} {author:<15} {book.copies_sold:<7} ${revenue:.0f}")
            
            # Genre analysis
            print("\\n📊 GENRE PERFORMANCE ANALYSIS")
            genre_stats = self.db.session.query(
                Book.genre,
                func.count(func.distinct(Book.book_id)).label('unique_books'),
                func.sum(OrderItem.quantity).label('total_sold'),
                func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue'),
                func.avg(OrderItem.price_at_time).label('avg_price')
            ).join(OrderItem).group_by(Book.genre).order_by(
                func.sum(OrderItem.price_at_time * OrderItem.quantity).desc()
            ).all()
            
            print("Genre                   Books  Sold   Revenue     Avg Price")
            print("-" * 60)
            for genre in genre_stats:
                genre_name = (genre.genre or 'Unclassified')[:20]
                revenue = float(genre.revenue) if genre.revenue else 0
                avg_price = float(genre.avg_price) if genre.avg_price else 0
                print(f"{genre_name:<20} {genre.unique_books:<6} {genre.total_sold:<6} ${revenue:<9,.0f} ${avg_price:.2f}")
            
            # Price analysis
            print("\\n💰 PRICING ANALYSIS")
            price_ranges = [
                ("Under $15", 0, 15),
                ("$15-$25", 15, 25),
                ("$25-$35", 25, 35),
                ("$35-$50", 35, 50),
                ("Over $50", 50, 999)
            ]
            
            print("Price Range         Orders    Revenue     Avg Order")
            print("-" * 50)
            
            for range_name, min_price, max_price in price_ranges:
                if max_price == 999:
                    range_orders = self.db.session.query(
                        func.count(Order.order_id),
                        func.sum(Order.total_amount),
                        func.avg(Order.total_amount)
                    ).filter(Order.total_amount >= min_price).first()
                else:
                    range_orders = self.db.session.query(
                        func.count(Order.order_id),
                        func.sum(Order.total_amount),
                        func.avg(Order.total_amount)
                    ).filter(Order.total_amount >= min_price, Order.total_amount < max_price).first()
                
                if range_orders and range_orders[0]:
                    orders = range_orders[0]
                    revenue = float(range_orders[1]) if range_orders[1] else 0
                    avg_order = float(range_orders[2]) if range_orders[2] else 0
                    print(f"{range_name:<18} {orders:<8} ${revenue:<9,.0f} ${avg_order:.2f}")

    def analyze_customer_behavior(self):
        """Analyze customer purchasing behavior and segmentation"""
        print("\\n🎯 CUSTOMER BEHAVIOR ANALYSIS")
        print("=" * 60)
        
        with self.app.app_context():
            # Customer lifetime value analysis
            print("💎 CUSTOMER VALUE SEGMENTATION")
            
            customer_metrics = self.db.session.query(
                Order.user_id,
                func.count(Order.order_id).label('total_orders'),
                func.sum(Order.total_amount).label('lifetime_value'),
                func.avg(Order.total_amount).label('avg_order_value'),
                func.min(Order.order_date).label('first_order'),
                func.max(Order.order_date).label('last_order')
            ).group_by(Order.user_id).all()
            
            # Segment customers
            high_value = []
            regular = []
            occasional = []
            
            for customer in customer_metrics:
                ltv = float(customer.lifetime_value) if customer.lifetime_value else 0
                orders = customer.total_orders
                
                if ltv > 500 or orders > 15:
                    high_value.append(customer)
                elif ltv > 200 or orders > 5:
                    regular.append(customer)
                else:
                    occasional.append(customer)
            
            total_customers = len(customer_metrics)
            high_value_revenue = sum(float(c.lifetime_value) for c in high_value)
            regular_revenue = sum(float(c.lifetime_value) for c in regular)
            occasional_revenue = sum(float(c.lifetime_value) for c in occasional)
            total_customer_revenue = high_value_revenue + regular_revenue + occasional_revenue
            
            print(f"High-Value Customers: {len(high_value)} ({len(high_value)/total_customers*100:.1f}%)")
            print(f"  Revenue: ${high_value_revenue:,.2f} ({high_value_revenue/total_customer_revenue*100:.1f}%)")
            print(f"  Avg LTV: ${high_value_revenue/len(high_value):.2f}" if high_value else "  Avg LTV: $0.00")
            
            print(f"\\nRegular Customers: {len(regular)} ({len(regular)/total_customers*100:.1f}%)")
            print(f"  Revenue: ${regular_revenue:,.2f} ({regular_revenue/total_customer_revenue*100:.1f}%)")
            print(f"  Avg LTV: ${regular_revenue/len(regular):.2f}" if regular else "  Avg LTV: $0.00")
            
            print(f"\\nOccasional Customers: {len(occasional)} ({len(occasional)/total_customers*100:.1f}%)")
            print(f"  Revenue: ${occasional_revenue:,.2f} ({occasional_revenue/total_customer_revenue*100:.1f}%)")
            print(f"  Avg LTV: ${occasional_revenue/len(occasional):.2f}" if occasional else "  Avg LTV: $0.00")
            
            # Order frequency analysis
            print("\\n🔄 PURCHASE FREQUENCY PATTERNS")
            order_frequencies = [c.total_orders for c in customer_metrics]
            
            freq_distribution = {
                '1 order': len([f for f in order_frequencies if f == 1]),
                '2-3 orders': len([f for f in order_frequencies if 2 <= f <= 3]),
                '4-10 orders': len([f for f in order_frequencies if 4 <= f <= 10]),
                '11-20 orders': len([f for f in order_frequencies if 11 <= f <= 20]),
                '21+ orders': len([f for f in order_frequencies if f > 20])
            }
            
            for category, count in freq_distribution.items():
                percentage = (count / total_customers * 100) if total_customers > 0 else 0
                print(f"  {category}: {count} customers ({percentage:.1f}%)")

    def analyze_operational_metrics(self):
        """Analyze operational efficiency and order fulfillment"""
        print("\\n⚡ OPERATIONAL EFFICIENCY ANALYSIS")
        print("=" * 60)
        
        with self.app.app_context():
            # Order status distribution
            print("📋 ORDER FULFILLMENT STATUS")
            status_stats = self.db.session.query(
                Order.status,
                func.count(Order.order_id).label('count'),
                func.sum(Order.total_amount).label('revenue')
            ).group_by(Order.status).all()
            
            total_orders = sum(stat.count for stat in status_stats)
            
            print("Status          Orders    Percentage    Revenue")
            print("-" * 50)
            for stat in status_stats:
                percentage = (stat.count / total_orders * 100) if total_orders > 0 else 0
                revenue = float(stat.revenue) if stat.revenue else 0
                status_name = stat.status.title()
                print(f"{status_name:<14} {stat.count:<8} {percentage:<11.1f}% ${revenue:,.0f}")
            
            # Payment method analysis
            print("\\n💳 PAYMENT METHOD PREFERENCES")
            payment_stats = self.db.session.query(
                Order.payment_method,
                func.count(Order.order_id).label('count'),
                func.avg(Order.total_amount).label('avg_amount')
            ).group_by(Order.payment_method).all()
            
            print("Payment Method      Orders    Avg Order Value")
            print("-" * 45)
            for stat in payment_stats:
                method_name = stat.payment_method.replace('_', ' ').title() if stat.payment_method else 'Unknown'
                avg_amount = float(stat.avg_amount) if stat.avg_amount else 0
                percentage = (stat.count / total_orders * 100) if total_orders > 0 else 0
                print(f"{method_name:<18} {stat.count:<8} ({percentage:.1f}%) ${avg_amount:.2f}")
            
            # Shipping analysis
            print("\\n🚚 SHIPPING & DELIVERY INSIGHTS")
            
            # Free shipping utilization
            free_shipping_orders = Order.query.filter(Order.delivery_charge == 0).count()
            paid_shipping_orders = Order.query.filter(Order.delivery_charge > 0).count()
            
            if total_orders > 0:
                free_shipping_rate = (free_shipping_orders / total_orders) * 100
                print(f"Free Shipping Rate: {free_shipping_rate:.1f}% ({free_shipping_orders}/{total_orders} orders)")
                
                # Average shipping revenue
                total_shipping_revenue = self.db.session.query(func.sum(Order.delivery_charge)).scalar() or 0
                avg_shipping_per_order = float(total_shipping_revenue) / total_orders
                print(f"Avg Shipping per Order: ${avg_shipping_per_order:.2f}")
                print(f"Total Shipping Revenue: ${float(total_shipping_revenue):,.2f}")

    def generate_recommendations(self):
        """Generate actionable business recommendations"""
        print("\\n🎯 STRATEGIC RECOMMENDATIONS")
        print("=" * 60)
        
        with self.app.app_context():
            recommendations = []
            
            # Analyze top genres for inventory recommendations
            top_genres = self.db.session.query(
                Book.genre,
                func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue')
            ).join(OrderItem).group_by(Book.genre).order_by(
                func.sum(OrderItem.price_at_time * OrderItem.quantity).desc()
            ).limit(3).all()
            
            if top_genres:
                top_genre_names = [g.genre for g in top_genres]
                recommendations.append(f"📚 Focus inventory expansion on top-performing genres: {', '.join(top_genre_names)}")
            
            # Customer retention analysis
            total_customers = User.query.count()
            repeat_customers = self.db.session.query(func.count(func.distinct(Order.user_id))).filter(
                Order.user_id.in_(
                    self.db.session.query(Order.user_id).group_by(Order.user_id).having(func.count(Order.order_id) > 1)
                )
            ).scalar()
            
            if total_customers > 0:
                retention_rate = (repeat_customers / total_customers) * 100
                if retention_rate < 60:
                    recommendations.append(f"👥 Improve customer retention (current: {retention_rate:.1f}%) through loyalty programs")
                else:
                    recommendations.append(f"✅ Strong customer retention ({retention_rate:.1f}%) - maintain current strategies")
            
            # Average order value optimization
            avg_order_value = self.db.session.query(func.avg(Order.total_amount)).scalar()
            if avg_order_value and float(avg_order_value) < 75:
                recommendations.append(f"💰 Increase average order value (current: ${float(avg_order_value):.2f}) through bundling and upselling")
            
            # Seasonal strategy
            recommendations.append("🌟 Leverage seasonal trends: Boost marketing in Sept (back-to-school) and Nov-Dec (holidays)")
            
            # Payment and shipping
            free_shipping_threshold = 75  # Based on our shipping logic
            avg_order = float(avg_order_value) if avg_order_value else 0
            if avg_order < free_shipping_threshold:
                recommendations.append(f"🚚 Consider lowering free shipping threshold from ${free_shipping_threshold} to boost order values")
            
            print("💡 KEY RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")

def main():
    """Run comprehensive analytics report"""
    print("📊 ADVANCED BOOKSTORE ANALYTICS DASHBOARD")
    print("=" * 70)
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    analytics = BookstoreAnalytics()
    
    # Run all analysis modules
    analytics.generate_executive_summary()
    analytics.analyze_seasonal_trends()
    analytics.analyze_product_performance()
    analytics.analyze_customer_behavior()
    analytics.analyze_operational_metrics()
    analytics.generate_recommendations()
    
    print("\\n" + "=" * 70)
    print("📈 ANALYTICS REPORT COMPLETE")
    print("🌐 Access live dashboard at: http://127.0.0.1:5000/admin")
    print("=" * 70)

if __name__ == "__main__":
    main()
