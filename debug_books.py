#!/usr/bin/env python3
"""
Debug script to test book retrieval in Flask context
"""

from app import app
from model import db, Book, BookImage

def debug_books():
    """Debug book retrieval"""
    
    with app.app_context():
        print("🔍 DEBUGGING BOOK RETRIEVAL")
        print("=" * 50)
        
        # Test database connection
        try:
            book_count = Book.query.count()
            print(f"✅ Database connection: SUCCESS")
            print(f"📚 Total books in database: {book_count}")
        except Exception as e:
            print(f"❌ Database connection: FAILED - {e}")
            return
        
        # Test index route query
        try:
            books = Book.query.limit(6).all()
            print(f"📖 Books retrieved by index route: {len(books)}")
            
            if books:
                print("\n📚 SAMPLE BOOKS FROM INDEX ROUTE:")
                for i, book in enumerate(books, 1):
                    print(f"   {i}. '{book.title}' by {book.author} - ID: {book.book_id}")
                    print(f"      Price: ${book.price}, Stock: {book.stock}")
                    
                    # Check for images
                    main_image = BookImage.query.filter_by(book_id=book.book_id, is_main=True).first()
                    if main_image:
                        print(f"      Main Image: {main_image.image_url}")
                    else:
                        print(f"      Main Image: None (will use placeholder)")
                    print()
            else:
                print("❌ No books retrieved by index route!")
                
        except Exception as e:
            print(f"❌ Index route query: FAILED - {e}")
            return
        
        # Test all books
        try:
            all_books = Book.query.all()
            print(f"📖 All books in database: {len(all_books)}")
            
            if all_books and len(all_books) > 6:
                print(f"✅ Database has books, index route should work")
            elif len(all_books) <= 6:
                print(f"⚠️  Database has only {len(all_books)} books")
            else:
                print(f"❌ No books found in database!")
                
        except Exception as e:
            print(f"❌ All books query: FAILED - {e}")
        
        # Test image count
        try:
            image_count = BookImage.query.count()
            print(f"🖼️  Total book images: {image_count}")
            
            if image_count == 0:
                print("⚠️  No book images found - books will show placeholder images")
            
        except Exception as e:
            print(f"❌ Image query: FAILED - {e}")

if __name__ == '__main__':
    debug_books()
