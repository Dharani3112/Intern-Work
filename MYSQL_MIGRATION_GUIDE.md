# Flask Bookstore: SQLite to MySQL Migration Guide

This guide will help you migrate your Flask bookstore application from SQLite to MySQL.

## Prerequisites

1. **MySQL Server** - Install MySQL 8.0 or later
2. **Python 3.8+** - Ensure you have Python installed
3. **Existing SQLite Database** - Your current bookstore database

## Step-by-Step Migration Process

### Step 1: Install Dependencies

First, install the new requirements with MySQL support:

```bash
pip install -r requirements.txt
```

New dependencies added:
- `PyMySQL==1.1.0` - MySQL driver for Python
- `mysql-connector-python==8.2.0` - Alternative MySQL connector
- `python-dotenv==1.0.0` - Environment variable management

### Step 2: Configure Environment Variables

1. **Copy the provided `.env` file** to your project root
2. **Update the MySQL credentials** in `.env`:

```bash
# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=bookstore_db
MYSQL_USERNAME=bookstore_user
MYSQL_PASSWORD=YOUR_SECURE_PASSWORD_HERE

# Flask Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
SECRET_KEY=your-secret-key-for-sessions

# Database URL for MySQL
SQLALCHEMY_DATABASE_URI=mysql+pymysql://bookstore_user:YOUR_SECURE_PASSWORD_HERE@localhost:3306/bookstore_db
```

**⚠️ Important:** Replace `YOUR_SECURE_PASSWORD_HERE` with a secure password of your choice.

### Step 3: Setup MySQL Database

Run the MySQL setup script:

```bash
python setup_mysql.py
```

This script will:
- Create the `bookstore_db` database
- Create the `bookstore_user` with proper permissions
- Test the connection

When prompted, enter your MySQL root password.

### Step 4: Migrate Your Data

Run the migration script to transfer all data from SQLite to MySQL:

```bash
python migrate_to_mysql.py
```

This script will:
- ✅ Verify your SQLite database exists and has data
- 🏗️ Create all necessary MySQL tables
- 📦 Transfer all data while preserving relationships
- ✅ Verify the migration was successful

**Migration includes:**
- All 100+ books with details
- 19,000+ orders and order items
- User accounts and authentication data
- Reviews and ratings
- Shopping cart items
- Book images and metadata

### Step 5: Verify Migration

Check that everything migrated correctly:

```bash
python check_database.py
```

This will show:
- Database type (should show "MySQL")
- Record counts for all tables
- Data integrity verification

### Step 6: Test Your Application

Start the Flask application:

```bash
python app.py
```

The application should now:
- ✅ Connect to MySQL instead of SQLite
- ✅ Display all your existing books
- ✅ Show order history
- ✅ Maintain user accounts
- ✅ Preserve all functionality

## Troubleshooting

### Common Issues:

1. **MySQL Connection Error:**
   - Verify MySQL server is running
   - Check credentials in `.env` file
   - Ensure MySQL user has proper permissions

2. **Migration Fails:**
   - Check `migration.log` file for detailed errors
   - Verify SQLite database exists at `instance/shopping_site.db`
   - Ensure MySQL database was created successfully

3. **Application Won't Start:**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Check `.env` file configuration
   - Verify database connection string

### Performance Benefits of MySQL:

- **Better Concurrency:** Handle multiple users simultaneously
- **Improved Performance:** Faster queries on large datasets
- **Production Ready:** Suitable for deployment
- **Advanced Features:** Better indexing, transactions, and scalability

## Backup and Rollback

### Before Migration:
Your original SQLite database is preserved at `instance/shopping_site.db`

### To Rollback to SQLite:
1. Update `.env` file:
   ```bash
   SQLALCHEMY_DATABASE_URI=sqlite:///shopping_site.db
   ```
2. Restart the application

## Production Deployment

For production deployment with MySQL:

1. **Use Environment Variables** - Never hardcode credentials
2. **SSL Connections** - Enable SSL for database connections
3. **Connection Pooling** - Configure SQLAlchemy connection pool
4. **Monitoring** - Set up database monitoring and logging

## Next Steps

After successful migration:

1. **Test all functionality** thoroughly
2. **Monitor performance** compared to SQLite
3. **Setup regular backups** of your MySQL database
4. **Consider removing** SQLite database after confirming stability
5. **Update deployment scripts** for production

## Support

If you encounter issues:

1. Check the `migration.log` file for detailed error messages
2. Verify all prerequisites are met
3. Ensure MySQL server is properly configured
4. Test database connections manually

The migration preserves all your valuable data while upgrading to a production-ready database system!
