#!/usr/bin/env python3
"""
Add Sample Reviews to Books
Adds realistic reviews to books in the database
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from model import db, User, Book, Review

# Sample review templates
REVIEW_TEMPLATES = {
    5: [
        "Absolutely brilliant! This book exceeded all my expectations. {specific}",
        "One of the best books I've ever read. {specific} Highly recommend!",
        "Outstanding work by {author}. {specific} A must-read!",
        "Perfect book! {specific} Will definitely read more from this author.",
        "Exceptional storytelling! {specific} Five stars well deserved."
    ],
    4: [
        "Really enjoyed this book. {specific} Definitely worth reading.",
        "Great book with excellent {quality}. {specific} Would recommend.",
        "Very good read. {specific} Looking forward to more from {author}.",
        "Solid book overall. {specific} A few minor issues but still very good.",
        "Engaging and well-written. {specific} Good addition to my library."
    ],
    3: [
        "Decent book. {specific} Has its moments but could be better.",
        "Average read. {specific} Not bad but not outstanding either.",
        "Okay book. {specific} Some parts were good, others not so much.",
        "Mixed feelings about this one. {specific} Worth a read if you have time.",
        "It was alright. {specific} Not my favorite but readable."
    ],
    2: [
        "Disappointing. {specific} Expected much more from this book.",
        "Not great. {specific} Struggled to get through it.",
        "Below average. {specific} Would not recommend.",
        "Had high hopes but was let down. {specific} Not worth the time.",
        "Mediocre at best. {specific} Many better options available."
    ],
    1: [
        "Terrible book. {specific} Complete waste of time.",
        "Awful. {specific} Cannot recommend this to anyone.",
        "Really bad. {specific} One of the worst books I've read.",
        "Horrible writing. {specific} Avoid at all costs.",
        "Absolutely dreadful. {specific} Deeply regret purchasing this."
    ]
}

# Specific comments by genre
GENRE_SPECIFICS = {
    'Science Fiction': [
        "The world-building was incredible and the technology concepts were fascinating.",
        "Amazing sci-fi concepts that really make you think about the future.",
        "Loved the space exploration elements and alien encounters.",
        "The scientific accuracy was impressive while maintaining great storytelling.",
        "Perfect blend of hard science and adventure."
    ],
    'Fantasy': [
        "The magic system was well-developed and the world felt alive.",
        "Epic fantasy at its finest with memorable characters and quests.",
        "The mythology and lore were richly detailed and immersive.",
        "Loved the magical creatures and fantastical elements.",
        "Perfect escapist fantasy with great character development."
    ],
    'Mystery': [
        "The plot twists kept me guessing until the very end.",
        "Excellent detective work and clues that were fair but challenging.",
        "The mystery was well-crafted with a satisfying resolution.",
        "Great atmosphere and suspense throughout the investigation.",
        "Perfect whodunit with red herrings and clever deductions."
    ],
    'Romance': [
        "The chemistry between the characters was electric and believable.",
        "Beautiful love story with emotional depth and character growth.",
        "The romantic tension was perfectly paced and satisfying.",
        "Heartwarming story that made me believe in love again.",
        "Perfect blend of passion and emotional connection."
    ],
    'Thriller': [
        "Edge-of-your-seat suspense that kept me reading all night.",
        "Heart-pounding action and tension from start to finish.",
        "The psychological aspects were brilliantly executed.",
        "Couldn't put it down - genuine page-turner with great pacing.",
        "Intense thriller that delivered on all fronts."
    ],
    'Horror': [
        "Genuinely scary with an atmosphere that got under my skin.",
        "Perfect horror that builds dread without relying on cheap scares.",
        "The psychological horror elements were masterfully done.",
        "Creepy and unsettling in all the right ways.",
        "Had me sleeping with the lights on - excellent horror writing."
    ],
    'Historical Fiction': [
        "The historical details were meticulously researched and authentic.",
        "Beautiful portrayal of the time period with vivid descriptions.",
        "The historical setting was brought to life magnificently.",
        "Excellent blend of history and storytelling.",
        "Felt like traveling back in time - immersive historical narrative."
    ],
    'Contemporary Fiction': [
        "Relatable characters dealing with modern life's complexities.",
        "The contemporary themes resonated deeply with current issues.",
        "Beautifully written exploration of modern relationships.",
        "Thought-provoking look at contemporary society.",
        "The modern setting felt authentic and engaging."
    ],
    'Biography': [
        "Fascinating look into an extraordinary life.",
        "Well-researched biography that reads like a novel.",
        "Inspiring life story that motivated me personally.",
        "Excellent portrayal of a remarkable individual.",
        "The biographical details were comprehensive and engaging."
    ],
    'Business': [
        "Practical advice that I can apply to my career immediately.",
        "Excellent business insights backed by real-world examples.",
        "The strategies presented are actionable and effective.",
        "Great read for anyone in business or entrepreneurship.",
        "Solid business principles explained clearly and concisely."
    ]
}

# General qualities for reviews
QUALITIES = [
    "character development", "plot", "writing style", "pacing", "dialogue",
    "themes", "structure", "prose", "narrative", "storytelling"
]

def get_random_specific(book_genre, author_name):
    """Get a random specific comment based on genre"""
    if book_genre in GENRE_SPECIFICS:
        return random.choice(GENRE_SPECIFICS[book_genre])
    else:
        # General comments
        general_comments = [
            f"The {random.choice(QUALITIES)} really stood out to me.",
            "The story was engaging and well-paced throughout.",
            "The characters were well-developed and believable.",
            "The writing style was clear and enjoyable to read.",
            "The themes were thought-provoking and meaningful."
        ]
        return random.choice(general_comments)

def add_sample_reviews():
    """Add sample reviews to books"""
    
    with app.app_context():
        print("🔍 Adding Sample Reviews to Books...")
        print("=" * 50)
        
        # Get all users and books
        users = User.query.all()
        books = Book.query.all()
        
        if len(users) < 5:
            print("❌ Need at least 5 users to add realistic reviews")
            return
        
        reviews_added = 0
        
        # Add reviews to a random subset of books
        books_to_review = random.sample(books, min(50, len(books)))
        
        for book in books_to_review:
            # Each book gets 1-5 reviews
            num_reviews = random.choices([1, 2, 3, 4, 5], weights=[20, 30, 25, 15, 10])[0]
            
            # Select random users for reviews (no duplicates per book)
            review_users = random.sample(users, min(num_reviews, len(users)))
            
            for user in review_users:
                # Check if user already reviewed this book
                existing_review = Review.query.filter_by(
                    user_id=user.user_id, 
                    book_id=book.book_id
                ).first()
                
                if existing_review:
                    continue
                
                # Generate rating (weighted towards higher ratings)
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
                
                # Generate review text
                template = random.choice(REVIEW_TEMPLATES[rating])
                specific_comment = get_random_specific(book.genre, book.author)
                quality = random.choice(QUALITIES)
                
                review_text = template.format(
                    specific=specific_comment,
                    author=book.author,
                    quality=quality
                )
                
                # Random review date (within last 2 years)
                days_ago = random.randint(1, 730)
                review_date = datetime.now() - timedelta(days=days_ago)
                
                # Create review
                review = Review(
                    user_id=user.user_id,
                    book_id=book.book_id,
                    rating=rating,
                    description=review_text,
                    created_at=review_date
                )
                
                try:
                    db.session.add(review)
                    reviews_added += 1
                except Exception as e:
                    print(f"Error adding review: {e}")
                    db.session.rollback()
                    continue
        
        # Commit all reviews
        try:
            db.session.commit()
            print(f"✅ Successfully added {reviews_added} reviews!")
            
            # Update book ratings
            print("📊 Updating book average ratings...")
            updated_books = 0
            
            for book in books:
                reviews = Review.query.filter_by(book_id=book.book_id).all()
                if reviews:
                    avg_rating = sum(r.rating for r in reviews) / len(reviews)
                    book.rating_avg = round(avg_rating, 1)
                    updated_books += 1
            
            db.session.commit()
            print(f"✅ Updated ratings for {updated_books} books!")
            
            # Print summary
            print("\n" + "=" * 50)
            print("📊 REVIEW SUMMARY:")
            
            total_reviews = Review.query.count()
            print(f"   • Total Reviews: {total_reviews}")
            
            # Rating distribution
            for rating in range(1, 6):
                count = Review.query.filter_by(rating=rating).count()
                percentage = (count / total_reviews * 100) if total_reviews > 0 else 0
                stars = "⭐" * rating
                print(f"   • {stars} ({rating}): {count} reviews ({percentage:.1f}%)")
            
            # Books with most reviews
            print(f"\n🏆 BOOKS WITH MOST REVIEWS:")
            top_reviewed_books = db.session.query(
                Book.title,
                Book.author,
                db.func.count(Review.review_id).label('review_count'),
                db.func.avg(Review.rating).label('avg_rating')
            ).join(Review, Book.book_id == Review.book_id)\
             .group_by(Book.book_id)\
             .order_by(db.func.count(Review.review_id).desc())\
             .limit(10).all()
            
            for i, (title, author, count, avg_rating) in enumerate(top_reviewed_books, 1):
                print(f"   {i:2d}. '{title}' by {author} - {count} reviews (avg: {avg_rating:.1f}⭐)")
            
            print(f"\n🎉 REVIEWS SUCCESSFULLY ADDED!")
            print(f"   Your bookstore now has realistic customer reviews!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing reviews: {e}")

if __name__ == '__main__':
    add_sample_reviews()
