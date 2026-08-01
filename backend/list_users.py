import sqlite3
conn = sqlite3.connect('beatpush.db')
cursor = conn.cursor()
cursor.execute('SELECT email, role, username FROM users')
for row in cursor.fetchall():
    print(f'{row[0]} | {row[1]} | {row[2]}')
