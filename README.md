# Flask E-Commerce Application

A full-featured e-commerce web application built with Flask, featuring product browsing, shopping cart functionality, user authentication, and checkout system.

## 🚀 Features

### Core Functionality
- **Product Catalog**: Browse and search products with categories
- **Shopping Cart**: Add/remove items with quantity management
- **User Authentication**: Registration and login system
- **Product Details**: Detailed product pages with reviews and ratings
- **Checkout System**: Complete order placement with shipping and payment
- **Responsive Design**: Mobile-friendly interface

### Product Management
- Featured products display
- Category-based browsing (Electronics, Fashion, Home & Garden, Sports, Books, Health & Beauty)
- Product search with filters (price range, category, keywords)
- Product reviews and ratings system
- Related products suggestions

### User Experience
- Session-based cart management
- Free shipping on orders over $50
- Real-time cart counter in header
- Intuitive navigation and modern UI
- Product image placeholders
- Order summary calculations

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── model.py              # SQLAlchemy database models
├── requirements.txt      # Python dependencies
├── static/
│   └── css/
│       └── styles.css    # Application styling
└── templates/
    ├── base.html         # Base template layout
    ├── index.html        # Homepage
    ├── product.html      # Product detail page
    ├── search.html       # Search results page
    ├── cart.html         # Shopping cart page
    ├── login.html        # User login page
    ├── signup.html       # User registration page
    └── shipping.html     # Checkout page
```

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3
- **Database ORM**: SQLAlchemy (MySQL ready)
- **Frontend**: HTML5, CSS3, Jinja2 Templates
- **Session Management**: Flask Sessions
- **Database**: MySQL (configured but using in-memory data for demo)

## 📋 Requirements

```
Flask==2.3.3
Werkzeug==2.3.7
```

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
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
   - Open your browser and go to: `http://localhost:5000`

## 🗄️ Database Models

The application includes comprehensive database models in `model.py`:

### Core Models
- **User**: User accounts with authentication
- **Product**: Product catalog with details and pricing
- **ProductImage**: Product image management
- **Review**: Customer reviews and ratings
- **CartItem**: Shopping cart functionality
- **Order**: Order management
- **Payment**: Payment processing
- **Address**: User shipping addresses

### Database Configuration
- **Database**: MySQL with SQLAlchemy ORM
- **Connection**: `mysql+mysqlconnector://root:Dharani$1@localhost/shopping_site`
- **Features**: Foreign key relationships, constraints, timestamps

## 🎯 Application Routes

### Public Routes
- `/` - Homepage with featured products
- `/search` - Product search with filters
- `/product/<id>` - Individual product details
- `/cart` - Shopping cart management
- `/signup` - User registration
- `/login` - User authentication
- `/shipping` - Checkout process

### Cart Management
- `/add_to_cart/<id>` - Add product to cart
- `/remove_from_cart/<id>` - Remove product from cart

## 💾 Data Management

### Current Implementation
- **Demo Mode**: Uses in-memory sample data for products
- **Session Storage**: Cart items stored in Flask sessions
- **Sample Products**: 5 featured products with details

### Sample Products Include
1. Wireless Headphones ($99.99)
2. Smart Watch ($199.99)
3. Laptop Bag ($49.99)
4. Coffee Maker ($79.99)
5. Yoga Mat ($29.99)

## 🎨 Frontend Features

### Responsive Design
- Mobile-first approach
- Flexible grid layouts
- Touch-friendly interfaces
- Cross-browser compatibility

### UI Components
- Modern card-based product display
- Interactive buttons with hover effects
- Sticky navigation header
- Clean form designs
- Rating stars and progress bars
- Category filtering sidebar

### User Interface Elements
- Product cards with hover animations
- Search bar with real-time filtering
- Shopping cart with item counter
- Price calculations with delivery charges
- Security badges for checkout
- Benefits showcase for registration

## 🔧 Configuration

### Flask Settings
- **Debug Mode**: Enabled for development
- **Secret Key**: Configured for session management
- **Template Folder**: `templates/`
- **Static Folder**: `static/`

### Business Logic
- **Free Shipping**: Orders over $50
- **Delivery Charge**: $5.99 for orders under $50
- **Tax Calculation**: 8% tax on subtotal
- **Payment Methods**: Credit/Debit Card, PayPal, Cash on Delivery

## 🔮 Future Enhancements

### Planned Features
- **Database Integration**: Connect with actual MySQL database
- **User Authentication**: Complete login/logout functionality
- **Order Management**: Order history and tracking
- **Payment Gateway**: Real payment processing
- **Admin Panel**: Product and order management
- **Email Notifications**: Order confirmations and updates
- **Inventory Management**: Stock tracking and alerts
- **Advanced Search**: Filters by brand, rating, price range
- **Wishlist**: Save products for later
- **Product Images**: Real image upload and management

### Technical Improvements
- **API Integration**: RESTful API endpoints
- **Caching**: Redis for session and data caching
- **Security**: Password hashing and CSRF protection
- **Testing**: Unit and integration tests
- **Deployment**: Production-ready configuration
- **Performance**: Database query optimization

## 🚨 Current Limitations

1. **Database**: Using sample data instead of MySQL connection
2. **Authentication**: Login functionality partially implemented
3. **Images**: Placeholder images instead of real product photos
4. **Payment**: Demo checkout without actual payment processing
5. **Orders**: No persistent order storage
6. **Email**: No email notifications system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of an internship/learning exercise. Please check with the project maintainer for licensing information.

## 📞 Support

For questions or issues:
1. Check the code comments for implementation details
2. Review the Flask and SQLAlchemy documentation
3. Test the application in development mode
4. Verify all dependencies are correctly installed

## 🏗️ Development Notes

### Code Structure
- **Modular Design**: Separated models, routes, and templates
- **Clean Code**: Well-commented and organized
- **Standards**: Follows Flask best practices
- **Scalability**: Designed for easy feature addition

### Debugging
- Flask debug mode enabled
- Detailed error messages
- Console logging for development
- Session debugging capabilities

---

**Last Updated**: May 2025  
**Version**: 1.0.0  
**Status**: Development/Demo Phase
