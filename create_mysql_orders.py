#!/usr/bin/env python3
"""
Create Fresh Order Data for MySQL Database
Generates realistic order and order_items data directly in MySQL without using SQLite.
"""

import random
import string
from datetime import datetime, timedelta
from model import app, db, User, Book, Order, OrderItem
import sys

def generate_tracking_number():
    """Generate realistic tracking number"""
    prefix = random.choice(['TRK', 'FDX', 'UPS', 'DHL', 'USPS'])
    suffix = ''.join(random.choices(string.digits, k=10))
    return f"{prefix}{suffix}"

def generate_address():
    """Generate realistic shipping addresses"""
    streets = [
        "123 Main Street", "456 Oak Avenue", "789 Pine Road", "321 Elm Street",
        "654 Maple Drive", "987 Cedar Lane", "147 Birch Court", "258 Willow Way",
        "369 Spruce Street", "741 Aspen Circle", "852 Cherry Lane", "963 Walnut Drive",
        "159 Hickory Road", "357 Poplar Avenue", "753 Sycamore Street", "951 Magnolia Drive"
    ]
    
    cities = [
        ("New York", "NY", "10001"), ("Los Angeles", "CA", "90210"), ("Chicago", "IL", "60601"),
        ("Houston", "TX", "77001"), ("Phoenix", "AZ", "85001"), ("Philadelphia", "PA", "19101"),
        ("San Antonio", "TX", "78201"), ("San Diego", "CA", "92101"), ("Dallas", "TX", "75201"),
        ("San Jose", "CA", "95101"), ("Austin", "TX", "73301"), ("Jacksonville", "FL", "32099"),
        ("Fort Worth", "TX", "76101"), ("Columbus", "OH", "43085"), ("Charlotte", "NC", "28201"),
        ("San Francisco", "CA", "94102"), ("Indianapolis", "IN", "46201"), ("Seattle", "WA", "98101"),
        ("Denver", "CO", "80014"), ("Washington", "DC", "20001")
    ]
    
    street = random.choice(streets)
    city, state, zip_code = random.choice(cities)
    
    return f"{street}, {city}, {state} {zip_code}, USA"

def create_fresh_orders():
    """Create fresh order data directly in MySQL"""
    print("🛒 Creating Fresh Order Data for MySQL Database")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check current state
            current_orders = Order.query.count()
            current_items = OrderItem.query.count()
            users = User.query.all()
            books = Book.query.all()
            
            print(f"📊 Current State:")
            print(f"   MySQL Orders: {current_orders}")
            print(f"   MySQL Order Items: {current_items}")
            print(f"   Available Users: {len(users)}")
            print(f"   Available Books: {len(books)}")
            
            if not users:
                print("❌ No users found! Please ensure users are created first.")
                return False
            
            if not books:
                print("❌ No books found! Please ensure books are created first.")
                return False
            
            # Ask for confirmation to create new data
            if current_orders > 0:
                print(f"\n⚠️  Warning: {current_orders} orders already exist in MySQL.")
                print("This will create additional orders.")
                proceed = input("Do you want to proceed? (y/N): ").lower().strip()
                if proceed != 'y':
                    print("Operation cancelled.")
                    return False
            
            # Order generation parameters
            num_orders = int(input(f"\nHow many orders to create? (recommended: 500-2000): ") or "1000")
            days_back = int(input("How many days of order history? (recommended: 90-365): ") or "180")
            
            print(f"\n🔄 Creating {num_orders} orders spanning {days_back} days...")
            
            # Order statuses with realistic distribution
            order_statuses = [
                ('completed', 0.70),    # 70% completed
                ('shipped', 0.15),      # 15% shipped
                ('processing', 0.08),   # 8% processing
                ('delivered', 0.05),    # 5% delivered
                ('cancelled', 0.02)     # 2% cancelled
            ]
            
            # Payment methods
            payment_methods = [
                ('credit_card', 0.60),
                ('debit_card', 0.25),
                ('paypal', 0.10),
                ('cash_on_delivery', 0.05)
            ]
            
            # Generate orders
            orders_created = 0
            items_created = 0
            
            for i in range(num_orders):
                try:
                    # Random order date within the specified range
                    days_ago = random.randint(0, days_back)
                    order_date = datetime.now() - timedelta(days=days_ago)
                    
                    # Random user
                    user = random.choice(users)
                    
                    # Random status (weighted)
                    status = random.choices(
                        [s[0] for s in order_statuses],
                        weights=[s[1] for s in order_statuses]
                    )[0]
                    
                    # Random payment method (weighted)
                    payment_method = random.choices(
                        [p[0] for p in payment_methods],
                        weights=[p[1] for p in payment_methods]
                    )[0]
                    
                    # Generate delivery date (for completed/delivered orders)
                    delivery_date = None
                    if status in ['completed', 'delivered']:
                        delivery_days = random.randint(2, 14)
                        delivery_date = order_date + timedelta(days=delivery_days)
                        if delivery_date > datetime.now():
                            delivery_date = None
                    
                    # Random number of books per order (1-5 books, weighted towards 1-2)
                    num_books = random.choices([1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.2, 0.07, 0.03])[0]
                    order_books = random.sample(books, min(num_books, len(books)))
                    
                    # Calculate order totals
                    subtotal = 0.0
                    order_items = []
                    
                    for book in order_books:
                        quantity = random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0]
                        price_at_time = float(book.price) if book.price else random.uniform(9.99, 49.99)
                        item_total = price_at_time * quantity
                        subtotal += item_total
                        
                        order_items.append({
                            'book': book,
                            'quantity': quantity,
                            'price_at_time': price_at_time
                        })
                    
                    # Calculate delivery charge
                    if subtotal >= 50:
                        delivery_charge = 0.0  # Free shipping over $50
                    else:
                        delivery_charge = random.choice([4.99, 6.99, 8.99])
                    
                    total_amount = subtotal + delivery_charge
                    
                    # Create order
                    order = Order(
                        user_id=user.user_id,
                        order_date=order_date,
                        delivery_date=delivery_date,
                        status=status,
                        subtotal=subtotal,
                        delivery_charge=delivery_charge,
                        total_amount=total_amount,
                        shipping_address=generate_address(),
                        payment_method=payment_method,
                        tracking_number=generate_tracking_number() if status in ['shipped', 'delivered', 'completed'] else None
                    )
                    
                    db.session.add(order)
                    db.session.flush()  # Get the order ID
                    
                    # Create order items
                    for item_data in order_items:
                        order_item = OrderItem(
                            order_id=order.order_id,
                            book_id=item_data['book'].book_id,
                            quantity=item_data['quantity'],
                            price_at_time=item_data['price_at_time']
                        )
                        db.session.add(order_item)
                        items_created += 1
                    
                    orders_created += 1
                    
                    # Commit in batches of 50 orders
                    if (i + 1) % 50 == 0:
                        db.session.commit()
                        print(f"   Progress: {i + 1}/{num_orders} orders created ({(i+1)/num_orders*100:.1f}%)")
                
                except Exception as e:
                    print(f"   Error creating order {i+1}: {e}")
                    db.session.rollback()
                    continue
            
            # Final commit
            db.session.commit()
            
            print(f"\n🎉 Order Creation Completed Successfully!")
            print("=" * 60)
            print(f"📊 Summary:")
            print(f"   ✅ Orders Created: {orders_created:,}")
            print(f"   ✅ Order Items Created: {items_created:,}")
            print(f"   📅 Date Range: {days_back} days")
            print(f"   💰 Estimated Total Revenue: ${total_amount * orders_created / num_orders:.2f}")
            
            # Verify final counts
            final_orders = Order.query.count()
            final_items = OrderItem.query.count()
            print(f"\n📈 Final Database Counts:")
            print(f"   Total Orders: {final_orders:,}")
            print(f"   Total Order Items: {final_items:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating orders: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

def verify_order_data():
    """Verify the created order data"""
    print("\n🔍 Verifying Order Data...")
    print("=" * 40)
    
    with app.app_context():
        try:
            # Basic counts
            total_orders = Order.query.count()
            total_items = OrderItem.query.count()
            total_users = User.query.count()
            total_books = Book.query.count()
            
            print(f"📊 Database Overview:")
            print(f"   Users: {total_users}")
            print(f"   Books: {total_books}")
            print(f"   Orders: {total_orders}")
            print(f"   Order Items: {total_items}")
            
            if total_orders > 0:
                # Sample order
                sample_order = Order.query.first()
                print(f"\n📋 Sample Order:")
                print(f"   Order ID: {sample_order.order_id}")
                print(f"   User ID: {sample_order.user_id}")
                print(f"   Date: {sample_order.order_date}")
                print(f"   Status: {sample_order.status}")
                print(f"   Total: ${sample_order.total_amount}")
                
                # Order items for sample order
                sample_items = OrderItem.query.filter_by(order_id=sample_order.order_id).all()
                print(f"   Items: {len(sample_items)}")
                
                # Status distribution
                from sqlalchemy import func
                status_stats = db.session.query(
                    Order.status,
                    func.count(Order.order_id).label('count')
                ).group_by(Order.status).all()
                
                print(f"\n📈 Order Status Distribution:")
                for status, count in status_stats:
                    percentage = (count / total_orders) * 100
                    print(f"   {status}: {count} ({percentage:.1f}%)")
                
                # Revenue calculation
                total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
                avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
                
                print(f"\n💰 Revenue Summary:")
                print(f"   Total Revenue: ${total_revenue:.2f}")
                print(f"   Average Order Value: ${avg_order_value:.2f}")
            
            print(f"\n✅ Verification completed!")
            
        except Exception as e:
            print(f"❌ Verification error: {e}")

def main():
    """Main function"""
    print("🛒 MYSQL ORDER DATA CREATOR")
    print("=" * 60)
    print("This script creates fresh order and order_items data directly in MySQL.")
    print("It does NOT use SQLite data - everything is generated new.")
    print()
    
    try:
        # Create fresh orders
        success = create_fresh_orders()
        
        if success:
            # Verify the data
            verify_order_data()
            
            print("\n🚀 SUCCESS!")
            print("=" * 60)
            print("✅ Fresh order data has been created in MySQL")
            print("✅ Your Flask bookstore now has realistic order history")
            print("✅ SQLite is no longer needed for order data")
            print("✅ Admin dashboard will show order analytics")
            print("✅ Users can place new orders")
            
            print("\n🎯 Next Steps:")
            print("1. Your Flask app is ready with fresh MySQL data")
            print("2. Visit: http://127.0.0.1:5000/admin/orders to see order analytics")
            print("3. Test placing new orders through the website")
            print("4. All order data is now stored in MySQL only")
            
        else:
            print("\n❌ Order creation failed!")
            
    except Exception as e:
        print(f"❌ Error in main process: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
