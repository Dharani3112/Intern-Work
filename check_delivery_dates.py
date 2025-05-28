from app import app, db
from model import Product

with app.app_context():
    products = Product.query.all()
    print('Products and their delivery dates:')
    for p in products:
        print(f'- {p.name}: {p.delivery_date} days')
    
    # Let's also check the first product specifically
    first_product = Product.query.first()
    if first_product:
        print(f'\nFirst product details:')
        print(f'Name: {first_product.name}')
        print(f'Delivery Date: {first_product.delivery_date}')
        print(f'Type: {type(first_product.delivery_date)}')
