from app import app
from model import db, Book, BookImage

# Sample books data
sample_books = [
    {
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'isbn': '978-0-7432-7356-5',
        'publisher': 'Scribner',
        'publication_year': 1925,
        'pages': 180,
        'language': 'English',
        'genre': 'Fiction',
        'format': 'Paperback',        'price': 12.99,
        'stock': 25,
        'description': 'A classic American novel set in the Jazz Age, exploring themes of wealth, love, idealism, and moral decay.',
        'delivery_date': 3
    },
    {
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'isbn': '978-0-06-112008-4',
        'publisher': 'J.B. Lippincott & Co.',
        'publication_year': 1960,
        'pages': 376,
        'language': 'English',
        'genre': 'Fiction',
        'format': 'Hardcover',        'price': 18.50,
        'stock': 30,
        'description': 'A gripping tale of racial injustice and childhood innocence in the American South.',
        'delivery_date': 2
    },
    {
        'title': '1984',
        'author': 'George Orwell',
        'isbn': '978-0-452-28423-4',
        'publisher': 'Signet Classics',
        'publication_year': 1949,
        'pages': 328,
        'language': 'English',
        'genre': 'Science Fiction',
        'format': 'Paperback',        'price': 13.95,
        'stock': 40,
        'description': 'A dystopian social science fiction novel about totalitarian control and surveillance.',
        'delivery_date': 3
    },
    {
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'isbn': '978-0-14-143951-8',
        'publisher': 'Penguin Classics',
        'publication_year': 1813,
        'pages': 432,
        'language': 'English',
        'genre': 'Romance',
        'format': 'Paperback',        'price': 11.99,
        'stock': 20,
        'description': 'A romantic novel about manners, marriage, and society in Georgian England.',
        'delivery_date': 4
    },
    {
        'title': 'The Catcher in the Rye',
        'author': 'J.D. Salinger',
        'isbn': '978-0-316-76948-0',
        'publisher': 'Little, Brown and Company',
        'publication_year': 1951,
        'pages': 277,
        'language': 'English',
        'genre': 'Fiction',
        'format': 'Hardcover',        'price': 16.99,
        'stock': 15,
        'description': 'A coming-of-age story following teenager Holden Caulfield in New York City.',
        'delivery_date': 3
    },
    {
        'title': 'Dune',
        'author': 'Frank Herbert',
        'isbn': '978-0-441-17271-9',
        'publisher': 'Ace Books',
        'publication_year': 1965,
        'pages': 688,
        'language': 'English',
        'genre': 'Science Fiction',
        'format': 'Paperback',        'price': 16.00,
        'stock': 35,
        'description': 'An epic science fiction novel set on the desert planet Arrakis.',
        'delivery_date': 5
    }
]

def add_sample_books():
    with app.app_context():
        # Clear existing books
        try:
            db.session.query(Book).delete()
            db.session.commit()
            
            for book_data in sample_books:
                book = Book(**book_data)
                db.session.add(book)
            
            db.session.commit()
            print(f"Added {len(sample_books)} sample books to the database!")
        except Exception as e:
            print(f"Error adding books: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_sample_books()