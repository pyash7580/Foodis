import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone, name, role FROM users WHERE phone LIKE '%9824948665%'")
    users = cursor.fetchall()
    print("Users found with 9824948665:", users)
    
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    print("Total restaurants:", cursor.fetchone()[0])
    
    conn.close()
except Exception as e:
    print("Error:", e)
