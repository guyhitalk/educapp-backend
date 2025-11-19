import sqlite3

conn = sqlite3.connect('educapp_users.db')
cursor = conn.cursor()

print("📋 Conversations table structure:")
cursor.execute("PRAGMA table_info(conversations);")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()