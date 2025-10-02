import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('quiz_app.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print('=== TABLES ===')
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f'- {table[0]}')

        print('\n=== USERS ===')
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        if users:
            for user in users:
                print(f'ID: {user["id"]}, Email: {user["email"]}, Name: {user["name"]}, Admin: {user["is_admin"]}')
        else:
            print('No users found')

        print('\n=== QUESTIONS COUNT ===')
        cursor.execute('SELECT COUNT(*) as count FROM questions')
        count = cursor.fetchone()
        print(f'Total questions: {count["count"]}')

        print('\n=== SAMPLE QUESTIONS ===')
        cursor.execute('SELECT id, question_text FROM questions LIMIT 3')
        questions = cursor.fetchall()
        for q in questions:
            print(f'Q{q["id"]}: {q["question_text"][:50]}...')

        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_database()