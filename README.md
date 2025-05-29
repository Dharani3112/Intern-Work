# 🛒 Flask E-Commerce Application

A comprehensive e-commerce web application built with Flask, featuring product management, user authentication, shopping cart, review system, and admin panel.

## 🚀 Features

### 🛍️ Core E-Commerce Features
- **Product Catalog**: Browse products with images, descriptions, and specifications
- **Advanced Search**: Filter products by name, category, and price range
- **Shopping Cart**: Add/remove items with real-time stock validation
- **User Authentication**: Complete signup/login system with session management
- **Order Processing**: Checkout with shipping information and inventory updates

### ⭐ Advanced Features
- **Product Reviews**: Users can rate and review products (1-5 stars)
- **Review Statistics**: Average ratings, review counts, and rating distribution
- **Dynamic Categories**: Database-driven category filtering
- **Stock Management**: Real inventory tracking and validation
- **Delivery Information**: Database-stored delivery timeframes
- **Admin Panel**: Complete product management with CRUD operations

### 🔧 Technical Features
- **REST API**: Complete API endpoints with JWT authentication
- **Database Integration**: SQLite with SQLAlchemy ORM
- **Session Management**: Hybrid cart storage (session + database)
- **Security**: Bcrypt password hashing and JWT tokens
- **CORS Support**: Cross-origin resource sharing enabled

## 🛠️ Technology Stack

- **Backend**: Flask 3.1.1
- **Database**: SQLite with SQLAlchemy ORM 3.1.1
- **Authentication**: Flask-Bcrypt 1.0.1 + JWT tokens 4.7.1
- **API**: RESTful endpoints with Flask-JWT-Extended
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Session Management**: Flask Sessions + Database storage
- **CORS**: Flask-CORS 6.0.0 for API access
- **Server**: Werkzeug 3.0.1

## 📋 Requirements

```
Flask==3.1.1
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.7.1
Flask-Bcrypt==1.0.1
Flask-CORS==6.0.0
Werkzeug==3.0.1
```

## 🚦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flask-ecommerce
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - **Store**: http://127.0.0.1:5000
   - **Admin Panel**: http://127.0.0.1:5000/admin/login
   - **API Health**: http://127.0.0.1:5000/api/health

## 🗄️ Database Configuration

- **Database**: SQLite with SQLAlchemy ORM
- **Connection**: `sqlite:///shopping_site.db`
- **Location**: `instance/shopping_site.db`
- **Features**: Foreign key relationships, constraints, timestamps
- **Models**: User, Product, ProductImage, Review, CartItem

### Database Models

1. **User**: User accounts with authentication
2. **Product**: Product catalog with pricing and inventory
3. **ProductImage**: Product images with main/secondary designation
4. **Review**: Product reviews with ratings and comments
5. **CartItem**: Shopping cart items for logged-in users

## 📁 Project Structure

```
flask-ecommerce/
├── app.py                     # Main Flask application
├── model.py                   # Database models
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── instance/
│   └── shopping_site.db      # SQLite database
├── static/
│   └── css/
│       └── styles.css        # Application styles
└── templates/                # Jinja2 templates
    ├── base.html             # Base template
    ├── index.html            # Homepage
    ├── product.html          # Product detail page
    ├── search.html           # Search results
    ├── cart.html             # Shopping cart
    ├── shipping.html         # Checkout page
    ├── login.html            # User login
    ├── signup.html           # User registration
    ├── forgot_password.html  # Password recovery    ├── admin_login.html      # Admin authentication
    ├── admin_dashboard.html  # Admin product list
    ├── admin_add_product.html # Add new product
    └── admin_edit_product.html # Edit existing product
```

## 🌐 Application Routes

### Public Routes
- `/` - Homepage with featured products
- `/search` - Product search with filters
- `/product/<id>` - Product detail page
- `/signup` - User registration
- `/login` - User login
- `/logout` - User logout
- `/forgot-password` - Password recovery

### User Routes (Login Required)
- `/cart` - Shopping cart
- `/shipping` - Checkout and order processing
- `/add_to_cart/<id>` - Add product to cart
- `/remove_from_cart/<id>` - Remove item from cart
- `/product/<id>/review` - Submit product review

### Admin Routes (Admin Password Required)
- `/admin/login` - Admin authentication
- `/admin` - Admin dashboard
- `/admin/logout` - Admin logout
- `/admin/product/add` - Add new products
- `/admin/product/edit/<id>` - Edit existing products
- `/admin/product/delete/<id>` - Remove products

### API Routes (JWT Authentication)
- `/api/health` - API health check
- `/api/products` - Get products with filtering
- `/api/products/<id>` - Get product details
- `/api/auth/signup` - User registration
- `/api/auth/login` - JWT authentication
- `/api/cart` - Cart management
- `/api/cart/add/<id>` - Add to cart

## 👤 Admin Access

**Default Admin Password**: `AdminSecure2025!`

### Admin Features
- ➕ **Add Products**: Create new products with images and details
- ✏️ **Edit Products**: Update product information and pricing
- 🗑️ **Delete Products**: Remove products from inventory
- 📊 **Manage Inventory**: Track stock levels and categories

## 🔐 Authentication

### User Authentication
- **Registration**: Email, username, password with validation
- **Login**: Email/password authentication with session management
- **Security**: Bcrypt password hashing
- **Sessions**: Flask sessions for web interface

### API Authentication
- **JWT Tokens**: JSON Web Tokens for API access
- **Token Expiry**: 1 hour (configurable)
- **Endpoints**: Separate API authentication routes

## 🛒 Shopping Cart

### Anonymous Users
- **Session Storage**: Cart items stored in Flask sessions
- **Persistence**: Items retained during browsing session
- **Transfer**: Cart transferred to database upon login

### Logged-in Users
- **Database Storage**: Cart items stored in database
- **Persistence**: Items retained across sessions
- **Stock Validation**: Real-time inventory checking

## ⭐ Review System

### Features
- **Star Ratings**: 1-5 star rating system
- **Comments**: Text reviews with user attribution
- **Statistics**: Average ratings and rating distribution
- **Validation**: Prevent duplicate reviews per user

### Display
- **Rating Bars**: Visual representation of rating distribution
- **Average Rating**: Calculated from all reviews
- **Review Count**: Total number of reviews
- **User Reviews**: Individual review display with timestamps

## 🔧 Configuration

### Environment Variables
```bash
JWT_SECRET_KEY=your-super-secret-jwt-key
SECRET_KEY=your-secret-key-for-sessions
```

### Database Configuration
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///shopping_site.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## 🧪 Testing

### Manual Testing
1. **Start the application**: `python app.py`
2. **Access homepage**: Navigate to http://127.0.0.1:5000
3. **Test user flow**: Register → Login → Browse → Add to Cart → Checkout
4. **Test admin flow**: Admin Login → Add/Edit/Delete Products
5. **Test API**: Use tools like Postman for API endpoints

### API Testing
```bash
# Health Check
curl http://127.0.0.1:5000/api/health

# Get Products
curl http://127.0.0.1:5000/api/products

# User Registration
curl -X POST http://127.0.0.1:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password"}'
```

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Set secure JWT and session secrets
2. **Database**: Consider PostgreSQL for production
3. **WSGI Server**: Use Gunicorn instead of Flask development server
4. **Reverse Proxy**: Configure Nginx for static files and load balancing
5. **SSL/TLS**: Enable HTTPS for secure authentication

### Sample Production Setup
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐛 Known Issues

1. **Payment Processing**: Currently demo-only, no real payment gateway integration
2. **Email Verification**: Registration doesn't include email verification
3. **Password Recovery**: Forgot password functionality is placeholder
4. **File Uploads**: Product images are URL-based, no file upload support

## 🔄 Future Enhancements

1. **Payment Integration**: Stripe/PayPal integration
2. **Email System**: Email verification and notifications
3. **File Upload**: Direct image upload for products
4. **Order History**: User order tracking and history
5. **Inventory Alerts**: Low stock notifications
6. **Product Categories**: Hierarchical category system
7. **Wishlist**: Product wishlist functionality
8. **Coupons**: Discount codes and promotions

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions and support, please create an issue in the repository or contact the development team.

---

**Last Updated**: May 29, 2025
**Version**: 2.0.0
**Status**: Production Ready