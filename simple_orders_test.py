#!/usr/bin/env python3
"""
Simple Orders Migration - Direct Approach
"""

import sqlite3
from model import app, db, Order, OrderItem
from datetime import datetime

def simple_orders_migration():
    print("Starting simple orders migration...")
    
    # Test database connections first
    try:
        sqlite_conn = sqlite3.connect('instance/shopping_site.db')
        print("✅ SQLite connection successful")
        
        # Test SQLite data
        cursor = sqlite_conn.execute('SELECT COUNT(*) FROM orders')
        sqlite_count = cursor.fetchone()[0]
        print(f"✅ SQLite has {sqlite_count} orders")
        
        with app.app_context():
            # Test MySQL connection
            mysql_count = Order.query.count()
            print(f"✅ MySQL has {mysql_count} orders")
            
            if mysql_count > 0:
                print("Orders already exist in MySQL")
                return
            
            print("Starting migration of first 10 orders...")
            
            # Get first 10 orders
            cursor = sqlite_conn.execute('''
                SELECT order_id, user_id, order_date, delivery_date, status,
                       subtotal, delivery_charge, total_amount, shipping_address,
                       payment_method, tracking_number
                FROM orders 
                LIMIT 10
            ''')
            orders = cursor.fetchall()
            
            for i, ord_row in enumerate(orders):
                print(f"Processing order {i+1}: ID {ord_row[0]}")
                
                # Handle dates
                order_date = datetime.now()
                if ord_row[2]:
                    try:
                        order_date = datetime.strptime(ord_row[2][:19], '%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                delivery_date = None
                if ord_row[3]:
                    try:
                        delivery_date = datetime.strptime(ord_row[3][:19], '%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                order = Order(
                    order_id=ord_row[0],
                    user_id=ord_row[1],
                    order_date=order_date,
                    delivery_date=delivery_date,
                    status=ord_row[4] or 'completed',
                    subtotal=float(ord_row[5]) if ord_row[5] else 0.0,
                    delivery_charge=float(ord_row[6]) if ord_row[6] else 0.0,
                    total_amount=float(ord_row[7]) if ord_row[7] else 0.0,
                    shipping_address=ord_row[8],
                    payment_method=ord_row[9],
                    tracking_number=ord_row[10]
                )
                
                db.session.add(order)
                print(f"  Added order {ord_row[0]} to session")
            
            # Commit all orders
            db.session.commit()
            print("✅ Committed 10 orders to MySQL")
            
            # Verify
            final_count = Order.query.count()
            print(f"✅ MySQL now has {final_count} orders")
            
        sqlite_conn.close()
        print("Migration test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    simple_orders_migration()
