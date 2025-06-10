#!/usr/bin/env python3
"""
Debug script to check books display issue
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from model import db, Book, BookImage

def test_books():
    """Test if books can be retrieved from database"""
    
    # Create a minimal Flask app for testing
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopping_site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("=== DEBUGGING BOOKS ISSUE ===")
        
        # Check total books
        total_books = Book.query.count()
        print(f"Total books in database: {total_books}")
        
        # Get first 6 books (same as index route)
        books = Book.query.limit(6).all()
        print(f"Books retrieved for homepage: {len(books)}")
        
        if books:
            print("\nBook details:")
            for i, book in enumerate(books, 1):
                print(f"  {i}. {book.title} by {book.author} (ID: {book.book_id})")
                print(f"     Price: ${book.price}, Stock: {book.stock}")
                
                # Check for images
                main_image = BookImage.query.filter_by(book_id=book.book_id, is_main=True).first()
                if main_image:
                    print(f"     Main image: {main_image.image_url}")
                else:
                    print(f"     No main image found")
                print()
        else:
            print("No books found!")
            
        # Check book images table
        total_images = BookImage.query.count()
        print(f"Total book images: {total_images}")
        
        if total_images == 0:
            print("⚠️  WARNING: No book images found! This might cause display issues.")
            print("Creating placeholder images for books...")
            
            # Create placeholder images for all books
            all_books = Book.query.all()
            for book in all_books:
                existing_image = BookImage.query.filter_by(book_id=book.book_id, is_main=True).first()
                if not existing_image:
                    placeholder_image = BookImage(
                        book_id=book.book_id,
                        image_url='static/images/placeholder.png',
                        is_main=True
                    )
                    db.session.add(placeholder_image)
            
            try:
                db.session.commit()
                print(f"✅ Created placeholder images for {len(all_books)} books")
            except Exception as e:
                print(f"❌ Error creating placeholder images: {e}")
                db.session.rollback()

if __name__ == "__main__":
    test_books()
