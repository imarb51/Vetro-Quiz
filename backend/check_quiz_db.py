import sqlite3

conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in quiz.db:', [t[0] for t in tables])

# If users table exists, check admin user
if any('users' in str(t) for t in tables):
    cursor.execute("SELECT id, email, name, is_admin FROM users WHERE email = 'admin@quiz.com'")
    admin = cursor.fetchone()
    print('Admin user:', admin if admin else 'Not found')

conn.close()
