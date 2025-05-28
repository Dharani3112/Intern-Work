from app import app, db
from model import User, Product, Review
from datetime import datetime

try:
    with app.app_context():
        # Get a test user and product
        user = User.query.filter_by(username='testuser').first()
        product = Product.query.first()
        
        if user and product:
            print(f"Test User: {user.username} ({user.email})")
            print(f"Test Product: {product.name}")
            
            # Check if user has already reviewed this product
            existing_review = Review.query.filter_by(
                user_id=user.user_id, 
                product_id=product.product_id
            ).first()
            
            if existing_review:
                print("✓ User has already reviewed this product")
            else:
                print("✗ User has not reviewed this product yet")
                
            # Show all reviews for this product
            reviews = Review.query.filter_by(product_id=product.product_id).all()
            print(f"\nTotal reviews for '{product.name}': {len(reviews)}")
            
            for review in reviews:
                reviewer = User.query.get(review.user_id)
                print(f"- {reviewer.username}: {review.rating}/5 - {review.description[:50]}...")
                
        else:
            print("Error: Test user or product not found")
            
except Exception as e:
    print(f"Error: {e}")
