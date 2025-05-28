from app import app, db
from model import Product

with app.app_context():
    try:
        # Get all products and update their delivery dates
        products = Product.query.all()
        print(f'Found {len(products)} products in database')
        
        if products:
            # Update the first few products with different delivery dates
            delivery_dates = [2, 5, 7, 3, 1]
            
            for i, product in enumerate(products[:5]):
                delivery_date = delivery_dates[i] if i < len(delivery_dates) else 7
                product.delivery_date = delivery_date
                print(f'Updated {product.name}: {delivery_date} days')
            
            db.session.commit()
            print('Successfully updated delivery dates!')
            
            # Show updated products
            print('\nUpdated products:')
            for product in products[:5]:
                print(f'- {product.name}: {product.delivery_date} days')
        else:
            print('No products found in database')
            
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()
