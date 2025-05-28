from app import app, db
from model import User

with app.app_context():
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
    else:
        print("Test user already exists!")
    
    # Show all users
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"- {user.username} ({user.email})")
