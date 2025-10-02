import sqlite3

conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# Delete all existing questions
cursor.execute("DELETE FROM questions")
conn.commit()

print('All questions deleted successfully')

# Verify
cursor.execute("SELECT COUNT(*) FROM questions")
count = cursor.fetchone()[0]
print(f'Questions remaining: {count}')

conn.close()
