from app import app, db
from model import User, Book, Order, OrderItem
from datetime import datetime, timedelta
from decimal import Decimal
import random

with app.app_context():
    print("Creating additional realistic orders...")
    
    users = User.query.all()
    books = Book.query.all()
    current_date = datetime(2025, 6, 10)
    
    print(f"Working with {len(users)} users and {len(books)} books")
    
    orders_created = 0
    
    # Create 150 more orders
    for i in range(150):
        # Random date - weighted toward recent
        if random.random() < 0.4:
            days_back = random.randint(1, 90)    # 40% in last 3 months
        elif random.random() < 0.7:
            days_back = random.randint(90, 270)  # 30% in 3-9 months ago
        else:
            days_back = random.randint(270, 730) # 30% in 9-24 months ago
        
        order_date = current_date - timedelta(days=days_back)
        user = random.choice(users)
        
        # Realistic status distribution
        if days_back > 30:
            status = random.choices(['completed', 'delivered'], weights=[75, 25])[0]
        elif days_back > 7:
            status = random.choices(['completed', 'delivered', 'shipped'], weights=[50, 30, 20])[0]
        else:
            status = random.choices(['pending', 'processing', 'shipped'], weights=[40, 35, 25])[0]
        
        # Payment method trends
        payment_method = random.choices(
            ['credit_card', 'debit_card', 'paypal', 'cash_on_delivery'],
            weights=[45, 25, 25, 5]
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
        
        # Add books (1-5 items per order)
        num_items = random.choices([1, 2, 3, 4, 5], weights=[35, 30, 20, 10, 5])[0]
        selected_books = random.sample(books, min(num_items, len(books)))
        
        subtotal = Decimal('0.00')
        
        for book in selected_books:
            # Most orders have 1 copy, some have 2-3
            quantity = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
            price = Decimal(str(book.price))
            
            # Occasional discounts
            if random.random() < 0.12:  # 12% chance of discount
                discount_percent = random.uniform(0.05, 0.25)  # 5-25% off
                price = price * Decimal(str(1 - discount_percent))
                price = price.quantize(Decimal('0.01'))
            
            # Create order item
            item = OrderItem(
                order_id=order.order_id,
                book_id=book.book_id,
                quantity=quantity,
                price_at_time=price
            )
            db.session.add(item)
            subtotal += price * quantity
        
        # Calculate shipping
        if subtotal > Decimal('60'):
            delivery_charge = Decimal('0.00')      # Free shipping over $60
        elif subtotal > Decimal('30'):
            delivery_charge = Decimal('3.99')      # Reduced shipping
        else:
            delivery_charge = Decimal('6.99')      # Standard shipping
        
        # Express shipping option (15% choose it)
        if random.random() < 0.15:
            delivery_charge += Decimal('9.99')
        
        total_amount = subtotal + delivery_charge
        
        # Update order totals
        order.subtotal = subtotal
        order.delivery_charge = delivery_charge
        order.total_amount = total_amount
        
        orders_created += 1
        
        # Progress updates and commits
        if orders_created % 25 == 0:
            print(f"Created {orders_created} orders...")
            db.session.commit()
    
    # Final commit
    db.session.commit()
    
    print(f"✅ Successfully created {orders_created} additional orders!")
    
    # Final statistics
    from sqlalchemy import func
    total_orders = Order.query.count()
    total_items = OrderItem.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar()
    avg_order_value = float(total_revenue) / total_orders if total_orders > 0 else 0
    
    print(f"\n📊 Final Database Statistics:")
    print(f"   Total Orders: {total_orders:,}")
    print(f"   Total Order Items: {total_items:,}")
    print(f"   Total Revenue: ${float(total_revenue):,.2f}")
    print(f"   Average Order Value: ${avg_order_value:.2f}")
    
    # Monthly breakdown for recent orders
    print(f"\n📈 Recent Order Distribution (Last 12 months):")
    recent_orders = db.session.execute("""
        SELECT 
            DATE_FORMAT(order_date, '%Y-%m') as month,
            COUNT(*) as order_count,
            SUM(total_amount) as revenue
        FROM orders 
        WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(order_date, '%Y-%m')
        ORDER BY month DESC
        LIMIT 12
    """).fetchall()
    
    for row in recent_orders:
        month, count, revenue = row
        print(f"   {month}: {count} orders, ${float(revenue):,.2f}")
