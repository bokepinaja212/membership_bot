import sqlite3

# Membuat database dan tabel
conn = sqlite3.connect('membership.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY,
    username TEXT,
    expiry_date DATE
)
''')

conn.commit()
conn.close()
print("Database berhasil dibuat!")