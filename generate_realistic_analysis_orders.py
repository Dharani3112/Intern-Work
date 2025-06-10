"""
Realistic Order Generator for Analytics
Creates a comprehensive dataset of orders with realistic patterns for pseudo-analysis.
Current date context: June 10, 2025
"""

import random
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from app import app, db
from model import User, Book, Order, OrderItem

class RealisticOrderGenerator:
    def __init__(self):
        self.current_date = datetime(2025, 6, 10)  # Current date context
        self.start_date = datetime(2023, 1, 1)    # 2.5 years of history
        
        # Customer behavior patterns
        self.customer_types = {
            'casual_reader': {'frequency': 0.4, 'avg_items': 1.5, 'price_sensitivity': 0.7},
            'book_lover': {'frequency': 0.3, 'avg_items': 3.2, 'price_sensitivity': 0.4},
            'gift_buyer': {'frequency': 0.15, 'avg_items': 2.1, 'price_sensitivity': 0.6},
            'bulk_buyer': {'frequency': 0.1, 'avg_items': 6.5, 'price_sensitivity': 0.3},
            'bargain_hunter': {'frequency': 0.05, 'avg_items': 2.8, 'price_sensitivity': 0.9}
        }
        
        # Seasonal multipliers by month
        self.seasonal_multipliers = {
            1: 0.7,   # January (post-holiday slump)
            2: 0.8,   # February
            3: 0.9,   # March
            4: 1.0,   # April
            5: 1.1,   # May
            6: 1.0,   # June
            7: 0.9,   # July (summer slowdown)
            8: 0.8,   # August
            9: 1.2,   # September (back to school)
            10: 1.1,  # October
            11: 1.4,  # November (Black Friday)
            12: 1.6   # December (Christmas)
        }
        
        # Genre popularity trends
        self.genre_trends = {
            'Fiction': {'base_popularity': 0.25, 'seasonal_boost': {'11': 0.3, '12': 0.4}},
            'Mystery': {'base_popularity': 0.15, 'seasonal_boost': {'10': 0.2}},
            'Romance': {'base_popularity': 0.12, 'seasonal_boost': {'2': 0.3, '6': 0.2}},
            'Science Fiction': {'base_popularity': 0.1, 'seasonal_boost': {}},
            'Fantasy': {'base_popularity': 0.1, 'seasonal_boost': {'12': 0.2}},
            'Biography': {'base_popularity': 0.08, 'seasonal_boost': {}},
            'History': {'base_popularity': 0.06, 'seasonal_boost': {}},
            'Self-Help': {'base_popularity': 0.05, 'seasonal_boost': {'1': 0.4, '9': 0.2}},
            'Business': {'base_popularity': 0.04, 'seasonal_boost': {'1': 0.3, '9': 0.2}},
            'Children': {'base_popularity': 0.05, 'seasonal_boost': {'12': 0.5}}
        }
    
    def assign_customer_types(self, users):
        """Assign customer types to users based on realistic distribution"""
        customer_assignments = {}
        
        for user in users:
            # Assign customer type based on probabilities
            rand = random.random()
            cumulative = 0
            
            for customer_type, props in self.customer_types.items():
                cumulative += props['frequency']
                if rand <= cumulative:
                    customer_assignments[user.user_id] = customer_type
                    break
        
        return customer_assignments
    
    def get_seasonal_factor(self, date):
        """Get seasonal multiplier for given date"""
        return self.seasonal_multipliers.get(date.month, 1.0)
    
    def get_weekday_factor(self, date):
        """Weekend vs weekday purchasing patterns"""
        weekday = date.weekday()
        if weekday == 6:  # Sunday
            return 1.3  # People browse and buy more on Sundays
        elif weekday == 5:  # Saturday
            return 1.1
        elif weekday in [0, 1]:  # Monday, Tuesday
            return 0.8
        else:
            return 1.0
    
    def select_books_for_customer(self, books, customer_type, date):
        """Select books based on customer type and seasonal preferences"""
        customer_props = self.customer_types[customer_type]
        
        # Determine number of items
        base_items = customer_props['avg_items']
        num_items = max(1, int(np.random.poisson(base_items)))
        num_items = min(num_items, 8)  # Cap at 8 items
        
        # Filter books by price sensitivity and genre preferences
        suitable_books = []
        
        for book in books:
            price = float(book.price)
            
            # Price filtering based on customer type
            if customer_type == 'bargain_hunter' and price > 20:
                continue
            elif customer_type == 'bulk_buyer' and price > 30:
                continue
            elif customer_type == 'casual_reader' and price > 25:
                continue
            
            # Genre seasonal boost
            genre_boost = 1.0
            if book.genre in self.genre_trends:
                genre_data = self.genre_trends[book.genre]
                month_str = str(date.month)
                if month_str in genre_data.get('seasonal_boost', {}):
                    genre_boost = 1 + genre_data['seasonal_boost'][month_str]
            
            # Add book with weight based on suitability
            weight = genre_boost * (1 + random.uniform(-0.2, 0.2))
            suitable_books.append((book, weight))
        
        # Select books based on weights
        if not suitable_books:
            suitable_books = [(book, 1.0) for book in books]
        
        books_with_weights = [(book, weight) for book, weight in suitable_books]
        weights = [weight for _, weight in books_with_weights]
        selected_books = []
        
        for _ in range(num_items):
            if books_with_weights:
                chosen_book = random.choices(books_with_weights, weights=weights, k=1)[0][0]
                selected_books.append(chosen_book)
                # Remove selected book to avoid duplicates in same order
                idx = next(i for i, (book, _) in enumerate(books_with_weights) if book == chosen_book)
                books_with_weights.pop(idx)
                weights.pop(idx)
        
        return selected_books
    
    def generate_realistic_orders(self, num_orders=500):
        """Generate realistic orders with sophisticated patterns"""
        
        with app.app_context():
            users = User.query.all()
            books = Book.query.all()
            
            if not users or not books:
                print("❌ No users or books found in database")
                return
            
            print(f"🚀 Generating {num_orders} realistic orders...")
            print(f"📊 Using {len(users)} users and {len(books)} books")
            
            # Assign customer types
            customer_assignments = self.assign_customer_types(users)
            
            # Generate orders distributed over time
            orders_created = 0
            total_revenue = Decimal('0.00')
            
            for i in range(num_orders):
                # Generate realistic date (weighted towards recent dates)
                days_back = int(np.random.exponential(120))  # Exponential distribution
                days_back = min(days_back, 900)  # Cap at ~2.5 years
                order_date = self.current_date - timedelta(days=days_back)
                
                # Skip if date is before our start date
                if order_date < self.start_date:
                    continue
                
                # Select user with some users being more active
                if random.random() < 0.3:  # 30% chance of repeat customer
                    # Weight towards users who already have orders
                    existing_customers = [u for u in users if Order.query.filter_by(user_id=u.user_id).first()]
                    if existing_customers:
                        user = random.choice(existing_customers)
                    else:
                        user = random.choice(users)
                else:
                    user = random.choice(users)
                
                customer_type = customer_assignments.get(user.user_id, 'casual_reader')
                
                # Calculate order probability based on various factors
                seasonal_factor = self.get_seasonal_factor(order_date)
                weekday_factor = self.get_weekday_factor(order_date)
                
                # Skip some orders based on realistic patterns
                if random.random() > seasonal_factor * weekday_factor * 0.7:
                    continue
                
                # Select books for this customer
                selected_books = self.select_books_for_customer(books, customer_type, order_date)
                
                if not selected_books:
                    continue
                
                # Determine order status based on date
                days_since_order = (self.current_date - order_date).days
                if days_since_order > 30:
                    status = random.choices(
                        ['completed', 'delivered', 'completed', 'completed'],
                        weights=[40, 30, 20, 10]
                    )[0]
                elif days_since_order > 7:
                    status = random.choices(
                        ['completed', 'delivered', 'shipped'],
                        weights=[50, 30, 20]
                    )[0]
                elif days_since_order > 2:
                    status = random.choices(
                        ['shipped', 'processing', 'delivered'],
                        weights=[60, 25, 15]
                    )[0]
                else:
                    status = random.choices(
                        ['pending', 'processing', 'shipped'],
                        weights=[50, 35, 15]
                    )[0]
                
                # Payment method based on trends over time
                if order_date.year >= 2024:
                    payment_method = random.choices(
                        ['credit_card', 'debit_card', 'paypal', 'cash_on_delivery'],
                        weights=[45, 25, 25, 5]
                    )[0]
                else:
                    payment_method = random.choices(
                        ['credit_card', 'debit_card', 'paypal', 'cash_on_delivery'],
                        weights=[40, 30, 15, 15]
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
                    # Realistic quantity distribution
                    if customer_type == 'bulk_buyer':
                        quantity = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 30, 25, 15])[0]
                    elif customer_type == 'gift_buyer':
                        quantity = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
                    else:
                        quantity = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
                    
                    # Occasional bulk purchases
                    if random.random() < 0.05:  # 5% chance of bulk order
                        quantity += random.randint(2, 5)
                    
                    price = Decimal(str(book.price))
                    
                    # Apply occasional discounts (seasonal sales, etc.)
                    if random.random() < 0.1:  # 10% chance of discount
                        discount = random.uniform(0.05, 0.25)  # 5-25% discount
                        price = price * Decimal(str(1 - discount))
                        price = price.quantize(Decimal('0.01'))
                    
                    order_item = OrderItem(
                        order_id=order.order_id,
                        book_id=book.book_id,
                        quantity=quantity,
                        price_at_time=price
                    )
                    db.session.add(order_item)
                    subtotal += price * quantity
                
                # Calculate delivery charge with realistic logic
                if subtotal > Decimal('75'):
                    delivery_charge = Decimal('0.00')  # Free shipping
                elif subtotal > Decimal('35'):
                    delivery_charge = Decimal('2.99')  # Reduced shipping
                else:
                    delivery_charge = Decimal('5.99')  # Standard shipping
                
                # Express shipping for some orders
                if random.random() < 0.15:  # 15% choose express
                    delivery_charge += Decimal('8.99')
                
                total = subtotal + delivery_charge
                
                order.subtotal = subtotal
                order.delivery_charge = delivery_charge
                order.total_amount = total
                
                total_revenue += total
                orders_created += 1
                
                if orders_created % 50 == 0:
                    print(f"✅ Created {orders_created} orders (${float(total_revenue):,.2f} revenue)...")
                    db.session.commit()  # Commit in batches
            
            # Final commit
            db.session.commit()
            
            print(f"\n🎉 Successfully generated {orders_created} realistic orders!")
            print(f"💰 Additional revenue: ${float(total_revenue):,.2f}")
            
            # Final statistics
            total_orders = Order.query.count()
            total_items = OrderItem.query.count()
            total_db_revenue = db.session.query(func.sum(Order.total_amount)).scalar()
            
            print(f"\n📈 Final Database Statistics:")
            print(f"   Total Orders: {total_orders:,}")
            print(f"   Total Order Items: {total_items:,}")
            print(f"   Total Revenue: ${float(total_db_revenue):,.2f}")
            print(f"   Average Order Value: ${float(total_db_revenue/total_orders):,.2f}")

if __name__ == '__main__':
    generator = RealisticOrderGenerator()
    generator.generate_realistic_orders(500)  # Generate 500 more realistic orders
