import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute("SELECT username, email FROM auth_user WHERE username='admin'")
row = cur.fetchone()
if row:
    print('Found admin:', row)
else:
    print('No admin user found')
conn.close()
