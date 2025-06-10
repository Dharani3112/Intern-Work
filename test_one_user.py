import sqlite3
from model import app, db, User

print('Starting migration...')

# Connect to SQLite
sqlite_conn = sqlite3.connect('instance/shopping_site.db')
sqlite_conn.row_factory = sqlite3.Row

# Get one user
cursor = sqlite_conn.execute('SELECT * FROM users LIMIT 1')
user_row = cursor.fetchone()
print(f'Found user: {user_row["username"]}')

# Add to MySQL
with app.app_context():
    existing = User.query.filter_by(user_id=user_row['user_id']).first()
    if not existing:
        new_user = User(
            user_id=user_row['user_id'],
            username=user_row['username'],
            email=user_row['email'],
            password_hash=user_row['password_hash'],
            first_name=user_row.get('first_name'),
            last_name=user_row.get('last_name'),
            mobile_number=user_row.get('mobile_number')
        )
        db.session.add(new_user)
        db.session.commit()
        print('User added to MySQL!')
        print(f'MySQL user count: {User.query.count()}')
    else:
        print('User already exists in MySQL')

sqlite_conn.close()
print('Migration test completed!')
