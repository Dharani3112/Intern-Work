#!/usr/bin/env python3
"""
Script to add sample reviews to the database for testing
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from model import User, Product, Review

def add_sample_reviews():
    with app.app_context():
        try:
            # First, let's create a test user if it doesn't exist
            test_user = User.query.filter_by(username='reviewer1').first()
            if not test_user:
                test_user = User(
                    username='reviewer1',
                    email='reviewer1@example.com',
                    first_name='John',
                    last_name='Doe'
                )
                test_user.set_password('password123')
                db.session.add(test_user)
                db.session.commit()
                print("Created test user: reviewer1")

            # Create another test user
            test_user2 = User.query.filter_by(username='reviewer2').first()
            if not test_user2:
                test_user2 = User(
                    username='reviewer2',
                    email='reviewer2@example.com',
                    first_name='Jane',
                    last_name='Smith'
                )
                test_user2.set_password('password123')
                db.session.add(test_user2)
                db.session.commit()
                print("Created test user: reviewer2")

            # Get the first product to add reviews to
            first_product = Product.query.first()
            if not first_product:
                print("No products found in database. Please add products first.")
                return

            print(f"Adding reviews to product: {first_product.name}")

            # Check if reviews already exist for this product
            existing_reviews = Review.query.filter_by(product_id=first_product.product_id).count()
            if existing_reviews > 0:
                print(f"Product already has {existing_reviews} reviews. Skipping...")
                return

            # Add sample reviews
            sample_reviews = [
                {
                    'user_id': test_user.user_id,
                    'product_id': first_product.product_id,
                    'rating': 5,
                    'description': 'Excellent product! Exceeded my expectations. Fast delivery and great quality.',
                },
                {
                    'user_id': test_user2.user_id,
                    'product_id': first_product.product_id,
                    'rating': 4,
                    'description': 'Good value for money. Minor issues with packaging but overall satisfied.',
                },
                {
                    'user_id': test_user.user_id,
                    'product_id': first_product.product_id,
                    'rating': 5,
                    'description': 'Amazing quality and fast shipping. Would definitely buy again!',
                },
                {
                    'user_id': test_user2.user_id,
                    'product_id': first_product.product_id,
                    'rating': 3,
                    'description': 'Average product. Does what it says but nothing special.',
                }
            ]

            for review_data in sample_reviews:
                review = Review(
                    user_id=review_data['user_id'],
                    product_id=review_data['product_id'],
                    rating=review_data['rating'],
                    description=review_data['description'],
                    created_at=datetime.now()
                )
                db.session.add(review)

            db.session.commit()
            print(f"Successfully added {len(sample_reviews)} sample reviews!")

            # Display the reviews we just added
            reviews = Review.query.filter_by(product_id=first_product.product_id).all()
            print(f"\nReviews for '{first_product.name}':")
            for review in reviews:
                user = User.query.get(review.user_id)
                print(f"- {user.username}: {review.rating}/5 stars - {review.description}")

        except Exception as e:
            print(f"Error adding sample reviews: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_sample_reviews()
