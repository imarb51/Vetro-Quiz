import sqlite3

conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# Delete broken admin user
cursor.execute("DELETE FROM users WHERE email = 'admin@quiz.com'")
conn.commit()

print('Admin user deleted successfully')

# Verify
cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@quiz.com'")
count = cursor.fetchone()[0]
print(f'Admin users remaining: {count}')

conn.close()
