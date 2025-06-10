@echo off
echo Starting Migration...
python -c "
import sqlite3
import sys
import os

print('Testing basic functionality...')
try:
    conn = sqlite3.connect('instance/shopping_site.db')
    cursor = conn.execute('SELECT COUNT(*) FROM books')
    count = cursor.fetchone()[0]
    print(f'SQLite has {count} books')
    conn.close()
    print('SQLite test passed')
except Exception as e:
    print(f'SQLite error: {e}')
    sys.exit(1)

try:
    from model import app, db, Book
    with app.app_context():
        mysql_count = Book.query.count()
        print(f'MySQL has {mysql_count} books')
    print('MySQL test passed')
except Exception as e:
    print(f'MySQL error: {e}')
    sys.exit(1)

print('All tests passed!')
"
echo Migration test completed.
pause
