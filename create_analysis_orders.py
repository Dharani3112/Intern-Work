"""
Enhanced Realistic Order Generator for Analytics
Creates orders with seasonal patterns, customer behavior, and realistic trends
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from app import app, db
from model import User, Book, Order, OrderItem

def exponential_random(scale=120):
    """Simple exponential distribution without numpy"""
    return int(-scale * random.log(1 - random.random()))

def generate_realistic_orders():
    print("🚀 Starting realistic order generation...")
    
    with app.app_context():
        users = User.query.all()
        books = Book.query.all()
        
        print(f"📊 Working with {len(users)} users and {len(books)} books")
        
        # Current date context
        current_date = datetime(2025, 6, 10)
        
        # Seasonal multipliers (higher in holiday months)
        seasonal_factors = {
            1: 0.7, 2: 0.8, 3: 0.9, 4: 1.0, 5: 1.1, 6: 1.0,
            7: 0.9, 8: 0.8, 9: 1.2, 10: 1.1, 11: 1.4, 12: 1.6
        }
        
        # Customer types with different behaviors
        customer_types = {
            'casual': {'weight': 0.4, 'avg_items': 2, 'max_price': 25},
            'enthusiast': {'weight': 0.3, 'avg_items': 4, 'max_price': 50},
            'gift_buyer': {'weight': 0.15, 'avg_items': 2, 'max_price': 40},
            'bulk_buyer': {'weight': 0.1, 'avg_items': 7, 'max_price': 35},
            'bargain_hunter': {'weight': 0.05, 'avg_items': 3, 'max_price': 15}
        }
        
        # Assign customer types to users
        user_types = {}
        for user in users:
            rand = random.random()
            cumulative = 0
            for customer_type, props in customer_types.items():
                cumulative += props['weight']
                if rand <= cumulative:
                    user_types[user.user_id] = customer_type
                    break
        
        orders_created = 0
        total_revenue = Decimal('0.00')
        
        # Generate 300 orders with realistic patterns
        for i in range(300):
            # Generate date with exponential distribution (more recent orders)
            days_back = min(exponential_random(90), 730)  # Max 2 years back
            order_date = current_date - timedelta(days=days_back)
            
            # Skip orders from before 2023
            if order_date.year < 2023:
                continue
            
            # Apply seasonal factor
            seasonal_mult = seasonal_factors.get(order_date.month, 1.0)
            if random.random() > seasonal_mult * 0.6:  # Skip some orders
                continue
            
            # Select user (some users order more frequently)
            if random.random() < 0.4:  # 40% repeat customers
                # Weight towards users with existing orders
                frequent_users = []
                for user in users:
                    existing_orders = Order.query.filter_by(user_id=user.user_id).count()
                    if existing_orders > 0:
                        frequent_users.extend([user] * min(existing_orders, 3))
                
                if frequent_users:
                    user = random.choice(frequent_users)
                else:
                    user = random.choice(users)
            else:
                user = random.choice(users)
            
            customer_type = user_types.get(user.user_id, 'casual')
            customer_props = customer_types[customer_type]
            
            # Determine order status based on age
            days_old = (current_date - order_date).days
            if days_old > 30:
                status = random.choices(['completed', 'delivered'], weights=[70, 30])[0]
            elif days_old > 7:
                status = random.choices(['completed', 'delivered', 'shipped'], weights=[50, 30, 20])[0]
            elif days_old > 2:
                status = random.choices(['shipped', 'processing', 'delivered'], weights=[50, 30, 20])[0]
            else:
                status = random.choices(['pending', 'processing'], weights=[60, 40])[0]
            
            # Payment method evolution over time
            if order_date.year >= 2024:
                payment_method = random.choices(
                    ['credit_card', 'debit_card', 'paypal', 'cash_on_delivery'],
                    weights=[50, 25, 20, 5]
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
            
            # Select books based on customer type
            max_price = customer_props['max_price']
            suitable_books = [b for b in books if float(b.price) <= max_price]
            
            if not suitable_books:
                suitable_books = books  # Fallback to all books
            
            # Number of items based on customer type
            base_items = customer_props['avg_items']
            num_items = max(1, base_items + random.randint(-1, 2))
            num_items = min(num_items, len(suitable_books), 8)  # Cap at 8
            
            selected_books = random.sample(suitable_books, num_items)
            subtotal = Decimal('0.00')
            
            # Add order items
            for book in selected_books:
                # Quantity distribution
                if customer_type == 'bulk_buyer':
                    quantity = random.choices([1, 2, 3, 4, 5], weights=[20, 25, 25, 20, 10])[0]
                else:
                    quantity = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
                
                price = Decimal(str(book.price))
                
                # Occasional discounts (10% chance)
                if random.random() < 0.1:
                    discount = random.uniform(0.05, 0.2)  # 5-20% off
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
            
            # Shipping logic
            if subtotal > Decimal('50'):
                delivery_charge = Decimal('0.00')  # Free shipping
            elif subtotal > Decimal('25'):
                delivery_charge = Decimal('3.99')  # Reduced shipping
            else:
                delivery_charge = Decimal('6.99')  # Standard shipping
            
            # Express shipping option (12% choose it)
            if random.random() < 0.12:
                delivery_charge += Decimal('9.99')
            
            total_amount = subtotal + delivery_charge
            
            order.subtotal = subtotal
            order.delivery_charge = delivery_charge
            order.total_amount = total_amount
            
            total_revenue += total_amount
            orders_created += 1
            
            if orders_created % 25 == 0:
                print(f"✅ Created {orders_created} orders (${float(total_revenue):,.2f} revenue)")
                db.session.commit()  # Commit in batches
        
        # Final commit
        db.session.commit()
        
        print(f"\\n🎉 Successfully created {orders_created} realistic orders!")
        print(f"💰 Additional revenue: ${float(total_revenue):,.2f}")
        
        # Show final stats
        from sqlalchemy import func
        total_orders = Order.query.count()
        total_items = OrderItem.query.count()
        total_db_revenue = db.session.query(func.sum(Order.total_amount)).scalar()
        avg_order_value = float(total_db_revenue) / total_orders
        
        print(f"\\n📈 Updated Database Statistics:")
        print(f"   Total Orders: {total_orders:,}")
        print(f"   Total Order Items: {total_items:,}")
        print(f"   Total Revenue: ${float(total_db_revenue):,.2f}")
        print(f"   Average Order Value: ${avg_order_value:.2f}")

if __name__ == '__main__':
    generate_realistic_orders()
