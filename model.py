from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database Configuration - MySQL Only
database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
if not database_uri:
    raise ValueError("SQLALCHEMY_DATABASE_URI environment variable is required for MySQL connection")

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    mobile_number = db.Column(db.String(20))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    pages = db.Column(db.Integer)
    language = db.Column(db.String(50), default='English')
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    delivery_date = db.Column(db.Integer)  # Delivery days
    genre = db.Column(db.String(100))  # Changed from category to genre
    format = db.Column(db.String(50), default='Paperback')  # Paperback, Hardcover, eBook
    rating_avg = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)

class BookImage(db.Model):
    __tablename__ = 'book_images'
    image_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    image_url = db.Column(db.Text)
    is_main = db.Column(db.Boolean, default=False)

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
    )

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    order_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='completed')  # pending, processing, shipped, delivered, completed, cancelled
    subtotal = db.Column(db.Numeric(10, 2))
    delivery_charge = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(10, 2))
    shipping_address = db.Column(db.Text)
    payment_method = db.Column(db.String(50))  # credit_card, debit_card, paypal, cash_on_delivery
    tracking_number = db.Column(db.String(100))
    
    # Relationships
    user = db.relationship('User', backref='orders')
    order_items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Numeric(10, 2))  # Price when order was placed
    
    # Relationships
    book = db.relationship('Book', backref='order_items')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Bookstore database tables created.")
