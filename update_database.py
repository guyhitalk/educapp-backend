import sqlite3
import os

def update_database():
    """Add conversations table to store chat history"""
    
    db_path = 'educapp_users.db'  # Updated to match copied database
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        subject TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_user_conversations 
    ON conversations(user_id, timestamp DESC)
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database updated successfully!")
    print("✅ Conversations table created")

if __name__ == "__main__":
    update_database()