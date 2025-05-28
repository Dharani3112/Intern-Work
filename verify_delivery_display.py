from app import app, db
from model import Product

try:
    with app.app_context():
        print("Current delivery information for all products:")
        print("=" * 50)
        
        products = Product.query.all()
        for product in products:
            delivery_info = f"Expected delivery: {product.delivery_date} business days" if product.delivery_date else "Delivery info not available"
            print(f"Product: {product.name}")
            print(f"  - Database delivery_date: {product.delivery_date}")
            print(f"  - Formatted message: {delivery_info}")
            print()
except Exception as e:
    print(f"Error: {e}")
