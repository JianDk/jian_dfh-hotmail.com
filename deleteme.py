import sqlite3
conn = sqlite3.Connection('orderDB.db')
c = conn.cursor()
c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='customer' ''')
print(c.fetchall())