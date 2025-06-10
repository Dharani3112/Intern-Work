#!/usr/bin/env python3
"""
Migrate Books Only
"""

import sqlite3
from model import app, db, Book

print("📚 Migrating Books to MySQL...")

# Connect to SQLite
sqlite_conn = sqlite3.connect('instance/shopping_site.db')

with app.app_context():
    try:
        # Check current count
        cursor = sqlite_conn.execute('SELECT COUNT(*) FROM books')
        sqlite_books = cursor.fetchone()[0]
        mysql_books = Book.query.count()
        
        print(f"SQLite books: {sqlite_books}")
        print(f"MySQL books: {mysql_books}")
        
        if mysql_books == 0 and sqlite_books > 0:
            print("Migrating books...")
            
            cursor = sqlite_conn.execute('''
                SELECT book_id, title, author, isbn, publisher, publication_year,
                       pages, language, description, price, delivery_date,
                       genre, format, rating_avg, stock
                FROM books LIMIT 10
            ''')
            books = cursor.fetchall()
            
            for book_row in books:
                book = Book(
                    book_id=book_row[0],
                    title=book_row[1],
                    author=book_row[2],
                    isbn=book_row[3],
                    publisher=book_row[4],
                    publication_year=book_row[5],
                    pages=book_row[6],
                    language=book_row[7] or 'English',
                    description=book_row[8],
                    price=float(book_row[9]) if book_row[9] else None,
                    delivery_date=book_row[10],
                    genre=book_row[11],
                    format=book_row[12] or 'Paperback',
                    rating_avg=float(book_row[13]) if book_row[13] else 0.0,
                    stock=book_row[14] or 0
                )
                db.session.add(book)
            
            db.session.commit()
            print(f"Successfully migrated {len(books)} books!")
            print(f"MySQL now has {Book.query.count()} books")
        else:
            print("Books already migrated or no books to migrate")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        sqlite_conn.close()

print("Books migration completed!")
