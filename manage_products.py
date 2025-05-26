#!/usr/bin/env python3
"""
Product Management Script for Flask E-commerce Application

This script provides functionality to:
- Add sample products to the database
- View existing products
- Add new products interactively
- Edit existing products
- Delete products

Usage:
    python manage_products.py [command]

Commands:
    add-samples    - Add sample products to database
    list          - List all products
    add           - Add a new product interactively
    edit <id>     - Edit product by ID
    delete <id>   - Delete product by ID
"""

import sys
from model import app, db, Product, ProductImage

def add_sample_products():
    """Add sample products to the database"""
    with app.app_context():
        # Check if products already exist
        if Product.query.count() > 0:
            print(f"Database already has {Product.query.count()} products.")
            response = input("Do you want to add more sample products? (y/n): ")
            if response.lower() != 'y':
                return

        sample_products = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'description': 'High-quality wireless headphones with noise cancellation and 30-hour battery life.',
                'specifications': 'Bluetooth 5.0, 30-hour battery, Active noise cancellation, Foldable design',
                'price': 89.99,
                'delivery_date': 3,
                'category': 'Electronics',
                'brand': 'AudioTech',
                'rating_avg': 4.5,
                'stock': 50,
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'
            },
            {
                'name': 'Smart Fitness Watch',
                'description': 'Advanced fitness tracker with heart rate monitoring, GPS, and smartphone integration.',
                'specifications': 'Heart rate monitor, GPS tracking, 7-day battery, Water resistant IP68',
                'price': 199.99,
                'delivery_date': 2,
                'category': 'Electronics',
                'brand': 'FitTech',
                'rating_avg': 4.3,
                'stock': 30,
                'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400'
            },
            {
                'name': 'Organic Cotton T-Shirt',
                'description': 'Comfortable, breathable organic cotton t-shirt available in multiple colors.',
                'specifications': '100% Organic cotton, Machine washable, Available in S-XXL',
                'price': 24.99,
                'delivery_date': 5,
                'category': 'Clothing',
                'brand': 'EcoWear',
                'rating_avg': 4.2,
                'stock': 100,
                'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400'
            },
            {
                'name': 'Professional Coffee Maker',
                'description': 'Programmable coffee maker with built-in grinder and thermal carafe.',
                'specifications': 'Built-in grinder, 12-cup capacity, Programmable timer, Thermal carafe',
                'price': 149.99,
                'delivery_date': 4,
                'category': 'Home & Kitchen',
                'brand': 'BrewMaster',
                'rating_avg': 4.6,
                'stock': 25,
                'image_url': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400'
            },
            {
                'name': 'Yoga Mat Premium',
                'description': 'Non-slip yoga mat made from eco-friendly materials with alignment guides.',
                'specifications': 'Eco-friendly TPE material, Non-slip surface, 6mm thickness, 72" length',
                'price': 39.99,
                'delivery_date': 3,
                'category': 'Sports & Fitness',
                'brand': 'ZenFit',
                'rating_avg': 4.4,
                'stock': 75,
                'image_url': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400'
            },
            {
                'name': 'Wireless Phone Charger',
                'description': 'Fast wireless charging pad compatible with all Qi-enabled devices.',
                'specifications': 'Qi wireless charging, 10W fast charging, LED indicator, Non-slip base',
                'price': 29.99,
                'delivery_date': 2,
                'category': 'Electronics',
                'brand': 'ChargeTech',
                'rating_avg': 4.1,
                'stock': 60,
                'image_url': 'https://images.unsplash.com/photo-1609592806596-b43bada2e3c9?w=400'
            }
        ]

        added_count = 0
        for product_data in sample_products:
            # Check if product already exists
            existing = Product.query.filter_by(name=product_data['name']).first()
            if existing:
                print(f"Product '{product_data['name']}' already exists, skipping...")
                continue

            # Create product
            image_url = product_data.pop('image_url')
            product = Product(**product_data)
            db.session.add(product)
            db.session.flush()  # Get the product ID

            # Add main image
            main_image = ProductImage(
                product_id=product.product_id,
                image_url=image_url,
                is_main=True
            )
            db.session.add(main_image)
            added_count += 1

        db.session.commit()
        print(f"Successfully added {added_count} sample products to the database!")

def list_products():
    """List all products in the database"""
    with app.app_context():
        products = Product.query.all()
        if not products:
            print("No products found in the database.")
            return

        print(f"\n{'ID':<5} {'Name':<30} {'Price':<10} {'Stock':<8} {'Category':<15}")
        print("-" * 70)
        for product in products:
            print(f"{product.product_id:<5} {product.name[:29]:<30} ${product.price:<9.2f} {product.stock:<8} {product.category:<15}")

def add_product_interactive():
    """Add a new product interactively"""
    with app.app_context():
        print("\n=== Add New Product ===")
        
        name = input("Product name: ").strip()
        if not name:
            print("Product name is required!")
            return

        description = input("Description: ").strip()
        specifications = input("Specifications: ").strip()
        
        try:
            price = float(input("Price: $"))
        except ValueError:
            print("Invalid price format!")
            return

        try:
            delivery_date = int(input("Delivery days: "))
        except ValueError:
            print("Invalid delivery days format!")
            return

        category = input("Category: ").strip()
        brand = input("Brand: ").strip()
        
        try:
            stock = int(input("Stock quantity: "))
        except ValueError:
            print("Invalid stock quantity!")
            return

        image_url = input("Main image URL (optional): ").strip()

        # Create product
        product = Product(
            name=name,
            description=description,
            specifications=specifications,
            price=price,
            delivery_date=delivery_date,
            category=category,
            brand=brand,
            stock=stock
        )
        
        db.session.add(product)
        db.session.flush()

        # Add image if provided
        if image_url:
            main_image = ProductImage(
                product_id=product.product_id,
                image_url=image_url,
                is_main=True
            )
            db.session.add(main_image)

        db.session.commit()
        print(f"Product '{name}' added successfully with ID {product.product_id}!")

def edit_product(product_id):
    """Edit an existing product"""
    with app.app_context():
        product = Product.query.get(product_id)
        if not product:
            print(f"Product with ID {product_id} not found!")
            return

        print(f"\n=== Editing Product: {product.name} ===")
        print("Press Enter to keep current value, or type new value:")

        # Edit fields
        new_name = input(f"Name [{product.name}]: ").strip()
        if new_name:
            product.name = new_name

        new_description = input(f"Description [{product.description}]: ").strip()
        if new_description:
            product.description = new_description

        new_price = input(f"Price [${product.price}]: ").strip()
        if new_price:
            try:
                product.price = float(new_price)
            except ValueError:
                print("Invalid price format, keeping current value.")

        new_stock = input(f"Stock [{product.stock}]: ").strip()
        if new_stock:
            try:
                product.stock = int(new_stock)
            except ValueError:
                print("Invalid stock format, keeping current value.")

        new_category = input(f"Category [{product.category}]: ").strip()
        if new_category:
            product.category = new_category

        new_brand = input(f"Brand [{product.brand}]: ").strip()
        if new_brand:
            product.brand = new_brand

        db.session.commit()
        print(f"Product '{product.name}' updated successfully!")

def delete_product(product_id):
    """Delete a product"""
    with app.app_context():
        product = Product.query.get(product_id)
        if not product:
            print(f"Product with ID {product_id} not found!")
            return

        print(f"Are you sure you want to delete '{product.name}'? (y/n): ", end="")
        confirm = input().strip().lower()
        
        if confirm == 'y':
            # Delete associated images first
            ProductImage.query.filter_by(product_id=product_id).delete()
            # Delete product
            db.session.delete(product)
            db.session.commit()
            print(f"Product '{product.name}' deleted successfully!")
        else:
            print("Deletion cancelled.")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == 'add-samples':
        add_sample_products()
    elif command == 'list':
        list_products()
    elif command == 'add':
        add_product_interactive()
    elif command == 'edit':
        if len(sys.argv) < 3:
            print("Usage: python manage_products.py edit <product_id>")
            return
        try:
            product_id = int(sys.argv[2])
            edit_product(product_id)
        except ValueError:
            print("Invalid product ID!")
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("Usage: python manage_products.py delete <product_id>")
            return
        try:
            product_id = int(sys.argv[2])
            delete_product(product_id)
        except ValueError:
            print("Invalid product ID!")
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == '__main__':
    main() 