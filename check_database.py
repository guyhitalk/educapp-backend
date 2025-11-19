import sqlite3

# Check educapp_users.db
conn = sqlite3.connect('educapp_users.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("📊 Tables in educapp_users.db:")
for table in tables:
    print(f"  - {table[0]}")
    
# Check users table structure
print("\n👤 Users table structure:")
cursor.execute("PRAGMA table_info(users);")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()