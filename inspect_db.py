import sqlite3
import os

db = "instance/campus_secondhand.db"
print(f"db exists: {os.path.exists(db)}")
if os.path.exists(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    print("tables:", [r[0] for r in cur.fetchall()])
    
    try:
        cur.execute("PRAGMA table_info(orders)")
        print("orders columns:", cur.fetchall())
        
        cur.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 5")
        print("last 5 orders:", cur.fetchall())
        
        cur.execute("SELECT user_id, COUNT(*) FROM orders GROUP BY user_id ORDER BY COUNT(*) DESC")
        print("orders per user:", cur.fetchall())
    except Exception as e:
        print(f"Error querying orders: {e}")
    
    conn.close()
