import sqlite3
import os

db_path = 'your_project/data/northwind.sqlite'
sql_path = 'your_project/data/create_views.sql'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open(sql_path, 'r') as f:
    sql_script = f.read()

try:
    cursor.executescript(sql_script)
    print("Views created successfully.")
except Exception as e:
    print(f"Error creating views: {e}")
finally:
    conn.close()
