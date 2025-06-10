"""
Simple batch order creator for analytics
"""
import random
from datetime import datetime, timedelta
from decimal import Decimal
from app import app, db
from model import User, Book, Order, OrderItem

def create_batch_orders():
    print("🎯 Creating comprehensive order dataset for analytics")
    
    with app.app_context():
        users = User.query.all()
        books = Book.query.all()
        current_count = Order.query.count()
        
        print(f"Current orders: {current_count}")
        print(f"Available users: {len(users)}")
        print(f"Available books: {len(books)}")
        
        target_orders = 250
        orders_created = 0
        
        print(f"Creating {target_orders} new orders...")
        
        try:
            for i in range(target_orders):
                # Random user
                user = random.choice(users)
                
                # Random date in past year
                days_ago = random.randint(1, 365)
                order_date = datetime.now() - timedelta(days=days_ago)
                
                # Order characteristics
                num_books = random.choices([1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.15, 0.1, 0.05])[0]
                selected_books = random.sample(books, min(num_books, len(books)))
                
                # Status based on age of order
                if days_ago > 90:
                    status = random.choices(['completed', 'delivered'], weights=[0.8, 0.2])[0]
                elif days_ago > 30:
                    status = random.choices(['completed', 'delivered', 'shipped'], weights=[0.6, 0.3, 0.1])[0]
                else:
                    status = random.choices(['pending', 'processing', 'shipped', 'delivered', 'completed'], 
                                         weights=[0.1, 0.2, 0.2, 0.25, 0.25])[0]
                
                payment_method = random.choices(['credit_card', 'debit_card', 'paypal', 'cash_on_delivery'], 
                                              weights=[0.5, 0.25, 0.2, 0.05])[0]
                
                # Create order
                order = Order(
                    user_id=user.user_id,
                    order_date=order_date,
                    status=status,
                    payment_method=payment_method
                )
                db.session.add(order)
                db.session.flush()
                
                # Add items
                subtotal = Decimal('0.00')
                for book in selected_books:
                    quantity = random.choices([1, 2, 3], weights=[0.75, 0.2, 0.05])[0]
                    price = Decimal(str(book.price))
                    
                    # Small price variations
                    if random.random() < 0.1:
                        variation = random.uniform(0.95, 1.05)
                        price = (price * Decimal(str(variation))).quantize(Decimal('0.01'))
                    
                    order_item = OrderItem(
                        order_id=order.order_id,
                        book_id=book.book_id,
                        quantity=quantity,
                        price_at_time=price
                    )
                    db.session.add(order_item)
                    subtotal += price * quantity
                
                # Delivery charges
                if subtotal >= Decimal('75'):
                    delivery_charge = Decimal('0.00')
                elif subtotal >= Decimal('40'):
                    delivery_charge = Decimal('5.99')
                else:
                    delivery_charge = Decimal('8.99')
                
                # Express shipping for some orders
                if random.random() < 0.15:  # 15% express shipping
                    delivery_charge += Decimal('7.00')
                
                total = subtotal + delivery_charge
                
                order.subtotal = subtotal
                order.delivery_charge = delivery_charge
                order.total_amount = total
                
                orders_created += 1
                
                # Commit in batches
                if orders_created % 50 == 0:
                    db.session.commit()
                    print(f"✅ Created {orders_created} orders...")
            
            # Final commit
            db.session.commit()
            
            # Statistics
            final_count = Order.query.count()
            total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar()
            avg_order = total_revenue / final_count if final_count > 0 else 0
            
            print(f"\n🎉 ORDER CREATION COMPLETE!")
            print(f"═" * 50)
            print(f"📊 Total Orders: {final_count}")
            print(f"💰 Total Revenue: ${float(total_revenue):.2f}")
            print(f"📈 Average Order: ${float(avg_order):.2f}")
            print(f"✨ New Orders Added: {orders_created}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    create_batch_orders()
