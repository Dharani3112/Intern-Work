from app import app
from model import db, Book

with app.app_context():
    count = db.session.query(Book).count()
    print(f"Books currently in database: {count}")
    
    # Get all books and list them
    books = db.session.query(Book).all()
    print(f"\nFirst 10 books in database:")
    for i, book in enumerate(books[:10], 1):
        print(f"{i}. {book.title} by {book.author}")
    
    print(f"\nLast 10 books in database:")
    for i, book in enumerate(books[-10:], count-9):
        print(f"{i}. {book.title} by {book.author}")
