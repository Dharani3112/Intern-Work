"""
Realistic Order Generator for Bookstore Analytics
Creates comprehensive order data with realistic customer behavior patterns
"""

import random
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from model import User, Book, Order, OrderItem

class RealisticOrderGenerator:
    def __init__(self):
        self.seasonal_multipliers = {
            # Higher sales during holiday seasons
            1: 0.8,   # January (post-holiday low)
            2: 0.9,   # February
            3: 1.0,   # March
            4: 1.1,   # April (spring reading)
            5: 1.2,   # May (Mother's Day, graduation)
            6: 1.0,   # June
            7: 0.9,   # July (summer vacation)
            8: 0.9,   # August
            9: 1.3,   # September (back to school)
            10: 1.1,  # October
            11: 1.4,  # November (Black Friday, pre-Christmas)
            12: 1.6   # December (Christmas shopping)
        }
        
        # Customer behavior profiles
        self.customer_profiles = {
            'casual_reader': {
                'frequency': 0.3,  # 30% of customers
                'orders_per_month': (0.5, 2),
                'books_per_order': (1, 2),
                'price_sensitivity': 0.7,
                'genre_preference': ['Fiction', 'Mystery', 'Romance']
            },
            'avid_reader': {
                'frequency': 0.25,  # 25% of customers
                'orders_per_month': (2, 4),
                'books_per_order': (2, 4),
                'price_sensitivity': 0.4,
                'genre_preference': ['Fiction', 'Science Fiction', 'Fantasy', 'Literary Fiction']
            },
            'academic': {
                'frequency': 0.2,   # 20% of customers
                'orders_per_month': (1, 3),
                'books_per_order': (1, 3),
                'price_sensitivity': 0.3,
                'genre_preference': ['Non-Fiction', 'Biography', 'History', 'Science']
            },
            'gift_buyer': {
                'frequency': 0.15,  # 15% of customers
                'orders_per_month': (0.2, 1),
                'books_per_order': (1, 3),
                'price_sensitivity': 0.5,
                'genre_preference': ['Fiction', 'Self-Help', 'Biography', 'Children']
            },
            'collector': {
                'frequency': 0.1,   # 10% of customers
                'orders_per_month': (1, 2),
                'books_per_order': (3, 8),
                'price_sensitivity': 0.2,
                'genre_preference': ['Fantasy', 'Science Fiction', 'Classic Literature', 'Poetry']
            }
        }
        
        # Order status probabilities
        self.status_probabilities = {
            'completed': 0.70,   # 70% completed orders
            'delivered': 0.15,   # 15% delivered
            'shipped': 0.08,     # 8% shipped
            'processing': 0.04,  # 4% processing
            'pending': 0.03      # 3% pending
        }
        
        # Payment method preferences
        self.payment_methods = {
            'credit_card': 0.45,
            'debit_card': 0.25,
            'paypal': 0.20,
            'cash_on_delivery': 0.10
        }

    def assign_customer_profiles(self, users):
        """Assign behavior profiles to users"""
        user_profiles = {}
        profile_names = list(self.customer_profiles.keys())
        profile_weights = [self.customer_profiles[p]['frequency'] for p in profile_names]
        
        for user in users:
            profile = random.choices(profile_names, weights=profile_weights)[0]
            user_profiles[user.user_id] = profile
            
        return user_profiles

    def get_genre_books(self, books):
        """Group books by genre for targeted selection"""
        genre_books = defaultdict(list)
        for book in books:
            genre = book.genre or 'Fiction'
            genre_books[genre].append(book)
        return dict(genre_books)

    def calculate_seasonal_factor(self, date):
        """Calculate seasonal sales multiplier"""
        return self.seasonal_multipliers.get(date.month, 1.0)

    def select_books_for_profile(self, profile_name, genre_books, num_books):
        """Select books based on customer profile preferences"""
        profile = self.customer_profiles[profile_name]
        preferred_genres = profile['genre_preference']
        
        selected_books = []
        attempts = 0
        max_attempts = num_books * 3
        
        while len(selected_books) < num_books and attempts < max_attempts:
            # Try preferred genres first
            genre = random.choice(preferred_genres) if random.random() < 0.8 else random.choice(list(genre_books.keys()))
            
            if genre in genre_books and genre_books[genre]:
                book = random.choice(genre_books[genre])
                if book not in selected_books:
                    selected_books.append(book)
            
            attempts += 1
        
        # Fill remaining slots with any books if needed
        all_books = [book for books in genre_books.values() for book in books]
        while len(selected_books) < num_books and all_books:
            book = random.choice(all_books)
            if book not in selected_books:
                selected_books.append(book)
        
        return selected_books

    def generate_realistic_orders(self, num_months=12, base_orders_per_month=50):
        """Generate realistic orders over specified time period"""
        print(f"🎯 Generating realistic orders for {num_months} months...")
        
        with app.app_context():
            # Get all users and books
            users = User.query.all()
            books = Book.query.all()
            
            if not users or not books:
                print("❌ No users or books found in database")
                return False
            
            print(f"📊 Working with {len(users)} users and {len(books)} books")
            
            # Assign customer profiles
            user_profiles = self.assign_customer_profiles(users)
            genre_books = self.get_genre_books(books)
            
            total_orders_created = 0
            start_date = datetime.now() - timedelta(days=num_months * 30)
            
            # Generate orders month by month
            for month in range(num_months):
                month_start = start_date + timedelta(days=month * 30)
                month_end = month_start + timedelta(days=29)
                
                # Calculate seasonal factor
                seasonal_factor = self.calculate_seasonal_factor(month_start)
                month_orders = int(base_orders_per_month * seasonal_factor)
                
                print(f"\n📅 Month {month + 1}: {month_start.strftime('%B %Y')} (Seasonal factor: {seasonal_factor:.1f})")
                print(f"   Target orders: {month_orders}")
                
                month_orders_created = 0
                
                # Create orders for this month
                for _ in range(month_orders):
                    # Select random user
                    user = random.choice(users)
                    profile_name = user_profiles[user.user_id]
                    profile = self.customer_profiles[profile_name]
                    
                    # Random date within the month
                    days_into_month = random.randint(0, 29)
                    order_date = month_start + timedelta(days=days_into_month)
                    
                    # Determine number of books based on profile
                    min_books, max_books = profile['books_per_order']
                    num_books = random.randint(min_books, max_books)
                    
                    # Select books based on profile
                    selected_books = self.select_books_for_profile(profile_name, genre_books, num_books)
                    
                    if not selected_books:
                        continue
                    
                    # Choose order status
                    status = random.choices(
                        list(self.status_probabilities.keys()),
                        weights=list(self.status_probabilities.values())
                    )[0]
                    
                    # Choose payment method
                    payment_method = random.choices(
                        list(self.payment_methods.keys()),
                        weights=list(self.payment_methods.values())
                    )[0]
                    
                    # Create order
                    order = Order(
                        user_id=user.user_id,
                        order_date=order_date,
                        status=status,
                        payment_method=payment_method
                    )
                    db.session.add(order)
                    db.session.flush()
                    
                    # Add order items
                    subtotal = Decimal('0.00')
                    for book in selected_books:
                        # Realistic quantity (mostly 1, sometimes 2-3)
                        quantity = 1
                        if random.random() < 0.2:  # 20% chance of multiple copies
                            quantity = random.randint(2, 3)
                        if profile_name == 'collector' and random.random() < 0.3:  # Collectors buy more
                            quantity = random.randint(1, 2)
                        
                        price = Decimal(str(book.price))
                        
                        # Apply price sensitivity (small random discount for price-sensitive customers)
                        if random.random() < profile['price_sensitivity'] * 0.1:
                            discount = Decimal('0.95')  # 5% discount
                            price = price * discount
                        
                        order_item = OrderItem(
                            order_id=order.order_id,
                            book_id=book.book_id,
                            quantity=quantity,
                            price_at_time=price
                        )
                        db.session.add(order_item)
                        subtotal += price * quantity
                    
                    # Calculate delivery charge (free over $50, realistic thresholds)
                    if subtotal >= Decimal('75'):
                        delivery_charge = Decimal('0.00')  # Free shipping
                    elif subtotal >= Decimal('35'):
                        delivery_charge = Decimal('4.99')  # Reduced shipping
                    else:
                        delivery_charge = Decimal('7.99')  # Standard shipping
                    
                    total_amount = subtotal + delivery_charge
                    
                    # Update order totals
                    order.subtotal = subtotal
                    order.delivery_charge = delivery_charge
                    order.total_amount = total_amount
                    
                    month_orders_created += 1
                    total_orders_created += 1
                
                # Commit month's orders
                db.session.commit()
                print(f"   ✅ Created {month_orders_created} orders")
            
            print(f"\n🎉 Successfully created {total_orders_created} realistic orders!")
            return True

    def generate_analytics_summary(self):
        """Generate summary statistics for analysis"""
        print("\n📈 ANALYTICS SUMMARY")
        print("=" * 50)
        
        with app.app_context():
            from sqlalchemy import func, extract
            
            # Basic counts
            total_orders = Order.query.count()
            total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or Decimal('0')
            avg_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0')
            
            print(f"📊 Total Orders: {total_orders}")
            print(f"💰 Total Revenue: ${total_revenue:.2f}")
            print(f"📈 Average Order Value: ${avg_order_value:.2f}")
            
            # Monthly breakdown
            print(f"\n📅 MONTHLY ORDER BREAKDOWN")
            monthly_stats = db.session.query(
                extract('year', Order.order_date).label('year'),
                extract('month', Order.order_date).label('month'),
                func.count(Order.order_id).label('order_count'),
                func.sum(Order.total_amount).label('revenue')
            ).group_by('year', 'month').order_by('year', 'month').all()
            
            for stat in monthly_stats[-12:]:  # Last 12 months
                month_name = datetime(int(stat.year), int(stat.month), 1).strftime('%B %Y')
                revenue = float(stat.revenue) if stat.revenue else 0
                print(f"   {month_name}: {stat.order_count} orders, ${revenue:.2f}")
            
            # Status breakdown
            print(f"\n📋 ORDER STATUS BREAKDOWN")
            status_stats = db.session.query(
                Order.status,
                func.count(Order.order_id).label('count'),
                func.sum(Order.total_amount).label('revenue')
            ).group_by(Order.status).all()
            
            for stat in status_stats:
                revenue = float(stat.revenue) if stat.revenue else 0
                print(f"   {stat.status.title()}: {stat.count} orders (${revenue:.2f})")
            
            # Top customers
            print(f"\n👥 TOP 10 CUSTOMERS BY ORDERS")
            top_customers = db.session.query(
                User.username,
                func.count(Order.order_id).label('order_count'),
                func.sum(Order.total_amount).label('total_spent')
            ).join(Order).group_by(User.user_id, User.username).order_by(func.count(Order.order_id).desc()).limit(10).all()
            
            for i, customer in enumerate(top_customers, 1):
                spent = float(customer.total_spent) if customer.total_spent else 0
                print(f"   {i}. {customer.username}: {customer.order_count} orders (${spent:.2f})")
            
            # Genre popularity (through order items)
            print(f"\n📚 POPULAR GENRES BY SALES")
            genre_stats = db.session.query(
                Book.genre,
                func.count(OrderItem.order_item_id).label('items_sold'),
                func.sum(OrderItem.quantity).label('books_sold'),
                func.sum(OrderItem.price_at_time * OrderItem.quantity).label('revenue')
            ).join(OrderItem).group_by(Book.genre).order_by(func.sum(OrderItem.price_at_time * OrderItem.quantity).desc()).all()
            
            for genre_stat in genre_stats[:10]:
                genre = genre_stat.genre or 'Unclassified'
                revenue = float(genre_stat.revenue) if genre_stat.revenue else 0
                print(f"   {genre}: {genre_stat.books_sold} books sold (${revenue:.2f})")

def main():
    print("📚 REALISTIC BOOKSTORE ORDER GENERATOR")
    print("=" * 60)
    
    generator = RealisticOrderGenerator()
    
    # Generate orders for last 12 months
    success = generator.generate_realistic_orders(num_months=12, base_orders_per_month=60)
    
    if success:
        # Generate analytics summary
        generator.generate_analytics_summary()
        print(f"\n✅ Order generation complete!")
        print(f"🌐 Access admin panel at: http://127.0.0.1:5000/admin")
        print(f"🔑 Admin password: admin123")
    else:
        print(f"\n❌ Order generation failed!")

if __name__ == "__main__":
    main()
