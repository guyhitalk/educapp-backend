import sqlite3
import shutil
from datetime import datetime

def fix_database():
    """Fix database schema to add missing columns"""
    
    db_path = 'educapp_users.db'
    
    # Backup first
    backup_path = f'educapp_users_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    shutil.copy(db_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if users table has id column
    cursor.execute("PRAGMA table_info(users);")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'id' not in columns:
        print("⚠️  Users table missing 'id' column. Recreating table...")
        
        # Create new users table with id
        cursor.execute('''
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            is_parent INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subscription_status TEXT DEFAULT 'free',
            subscription_start_date TIMESTAMP,
            stripe_customer_id TEXT,
            questions_this_month INTEGER DEFAULT 0,
            last_reset_date TEXT
        )
        ''')
        
        # Copy data from old table
        cursor.execute('''
        INSERT INTO users_new (email, password_hash, name, is_parent, created_at, 
                               subscription_status, subscription_start_date, 
                               stripe_customer_id, questions_this_month, last_reset_date)
        SELECT email, password_hash, name, is_parent, created_at,
               subscription_status, subscription_start_date,
               stripe_customer_id, questions_this_month, last_reset_date
        FROM users
        ''')
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE users')
        cursor.execute('ALTER TABLE users_new RENAME TO users')
        
        print("✅ Users table recreated with id column")
    else:
        print("✅ Users table already has id column")
    
    # Drop and recreate conversations table with correct schema
    cursor.execute('DROP TABLE IF EXISTS conversations')
    print("⚠️  Dropped old conversations table (wrong schema)")
    
    cursor.execute('''
    CREATE TABLE conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        subject TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE INDEX idx_user_conversations 
    ON conversations(user_id, timestamp DESC)
    ''')
    
    print("✅ Conversations table created with CORRECT schema")
    print("   - user_id (INTEGER)")
    print("   - question (TEXT)")
    print("   - answer (TEXT)")
    print("   - subject (TEXT)")
    print("   - timestamp (DATETIME)")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database schema fixed successfully!")
    print(f"✅ Backup saved as: {backup_path}")

if __name__ == "__main__":
    fix_database()