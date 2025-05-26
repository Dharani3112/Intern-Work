#!/usr/bin/env python3
"""
Sample data insertion script for the e-commerce application
"""

from app import app
from model import db, Product, ProductImage, User
import sys

def add_sample_products():
    """Add sample products to the database"""
    
    sample_products = [
        {
            'name': 'MacBook Pro 16"',
            'description': 'Apple MacBook Pro 16-inch with M2 Pro chip, 16GB RAM, and 512GB SSD. Perfect for professional work and creative tasks.',
            'specifications': 'M2 Pro chip, 16GB RAM, 512GB SSD, 16-inch Liquid Retina XDR display',
            'price': 2499.99,
            'delivery_date': 3,
            'category': 'Electronics',
            'brand': 'Apple',
            'stock': 15,
            'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500'
        },
        {
            'name': 'Nike Air Max 270',
            'description': 'Comfortable and stylish running shoes with Air Max cushioning technology. Available in multiple colors.',
            'specifications': 'Air Max cushioning, breathable mesh upper, rubber outsole',
            'price': 149.99,
            'delivery_date': 2,
            'category': 'Footwear',
            'brand': 'Nike',
            'stock': 50,
            'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500'
        },
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'description': 'Latest Samsung Galaxy smartphone with advanced camera system and S Pen functionality.',
            'specifications': 'Snapdragon 8 Gen 3, 12GB RAM, 256GB storage, 200MP camera',
            'price': 1199.99,
            'delivery_date': 1,
            'category': 'Electronics',
            'brand': 'Samsung',
            'stock': 25,
            'image_url': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500'
        },
        {
            'name': 'Levi\'s 501 Original Jeans',
            'description': 'Classic straight-leg jeans made from premium denim. Timeless style that never goes out of fashion.',
            'specifications': '100% cotton denim, straight leg, button fly',
            'price': 89.99,
            'delivery_date': 2,
            'category': 'Clothing',
            'brand': 'Levi\'s',
            'stock': 100,
            'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500'
        },
        {
            'name': 'KitchenAid Stand Mixer',
            'description': 'Professional-grade stand mixer perfect for baking and cooking. Includes multiple attachments.',
            'specifications': '5-quart bowl, 10 speeds, tilt-head design, multiple attachments included',
            'price': 379.99,
            'delivery_date': 5,
            'category': 'Home & Kitchen',
            'brand': 'KitchenAid',
            'stock': 20,
            'image_url': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500'
        },
        {
            'name': 'Adidas Ultraboost 22',
            'description': 'High-performance running shoes with Boost cushioning and Primeknit upper for maximum comfort.',
            'specifications': 'Boost midsole, Primeknit upper, Continental rubber outsole',
            'price': 179.99,
            'delivery_date': 3,
            'category': 'Footwear',
            'brand': 'Adidas',
            'stock': 35,
            'image_url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500'
        }
    ]
    
    try:
        # Check if products already exist
        existing_count = Product.query.count()
        if existing_count > 0:
            print(f"Database already has {existing_count} products. Skipping sample data insertion.")
            return
        
        print("Adding sample products to database...")
        
        for product_data in sample_products:
            # Create product
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                specifications=product_data['specifications'],
                price=product_data['price'],
                delivery_date=product_data['delivery_date'],
                category=product_data['category'],
                brand=product_data['brand'],
                stock=product_data['stock']
            )
            
            db.session.add(product)
            db.session.flush()  # Get the product ID
            
            # Add main image
            if product_data['image_url']:
                main_image = ProductImage(
                    product_id=product.product_id,
                    image_url=product_data['image_url'],
                    is_main=True
                )
                db.session.add(main_image)
            
            print(f"✓ Added: {product_data['name']}")
        
        db.session.commit()
        print(f"\n🎉 Successfully added {len(sample_products)} sample products!")
        print("You can now test the admin functionality and see dynamic categories in action.")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding sample products: {e}")
        return False
    
    return True

def add_sample_user():
    """Add a sample user for testing"""
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(email='test@example.com').first()
        if existing_user:
            print("Sample user already exists.")
            return
        
        print("Adding sample user...")
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            mobile_number='1234567890'
        )
        test_user.set_password('password123')
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✓ Added sample user: test@example.com (password: password123)")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding sample user: {e}")

def main():
    """Main function to add sample data"""
    print("🚀 Adding sample data to the e-commerce database...\n")
    
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # Add sample data
        add_sample_products()
        add_sample_user()
        
        print(f"\n📊 Database Summary:")
        print(f"   Products: {Product.query.count()}")
        print(f"   Users: {User.query.count()}")
        print(f"   Product Images: {ProductImage.query.count()}")
        
        print(f"\n🔐 Admin Access:")
        print(f"   URL: http://127.0.0.1:5000/admin/login")
        print(f"   Password: AdminSecure2025!")
        
        print(f"\n👤 Test User Login:")
        print(f"   Email: test@example.com")
        print(f"   Password: password123")

if __name__ == '__main__':
    main()
