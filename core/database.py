# core/database.py
import sqlite3
from datetime import datetime
import os

# Use educapp_users.db (the one we just fixed)
DB_PATH = 'educapp_users.db'

def init_database():
    """Initialize SQLite database with all tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table (with id column)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  name TEXT,
                  is_parent INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  subscription_status TEXT DEFAULT 'free',
                  subscription_start_date TIMESTAMP,
                  stripe_customer_id TEXT,
                  questions_this_month INTEGER DEFAULT 0,
                  last_reset_date TEXT)''')
    
    # Conversations table (using user_id, not email)
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  question TEXT NOT NULL,
                  answer TEXT NOT NULL,
                  subject TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Children table (for parent oversight)
    c.execute('''CREATE TABLE IF NOT EXISTS children
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  parent_email TEXT,
                  child_email TEXT,
                  child_name TEXT,
                  FOREIGN KEY (parent_email) REFERENCES users(email))''')
    
    # API Usage table
    c.execute('''CREATE TABLE IF NOT EXISTS api_usage
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_email TEXT,
                  input_tokens INTEGER,
                  output_tokens INTEGER,
                  estimated_cost REAL,
                  timestamp TIMESTAMP,
                  model TEXT DEFAULT 'claude-3-opus',
                  FOREIGN KEY (user_email) REFERENCES users(email))''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


def get_user_id_by_email(email: str) -> int:
    """Get user ID from email address"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0]
        return None
        
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None


def create_user(email, name, password=None):
    """Create a new user account with optional password"""
    import bcrypt
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Hash password if provided
    password_hash = None
    if password:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        c.execute('''INSERT INTO users (email, name, password_hash, created_at, subscription_status)
                     VALUES (?, ?, ?, ?, 'free')''',
                  (email, name, password_hash, datetime.now()))
        
        conn.commit()
        print(f"✅ User created: {email}")
        return True
    except sqlite3.IntegrityError:
        print(f"ℹ️ User already exists: {email}")
        return False
    finally:
        conn.close()


def verify_password(email, password):
    """Verify user password"""
    import bcrypt
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    
    if not result or not result[0]:
        return False
    
    stored_hash = result[0].encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)


def update_password(email, new_password):
    """Update user password"""
    import bcrypt
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    c.execute('UPDATE users SET password_hash = ? WHERE email = ?', 
              (password_hash, email))
    
    conn.commit()
    conn.close()
    print(f"✅ Password updated for: {email}")


def user_exists(email):
    """Check if user exists"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT email FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()
    
    return result is not None


def get_user(email):
    """Get user information"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    
    return user


def save_conversation(user_email, message, response, subject=None):
    """Save a conversation to the database (legacy function for compatibility)"""
    # This is kept for backward compatibility but now uses user_id internally
    user_id = get_user_id_by_email(user_email)
    if not user_id:
        print(f"Warning: Could not find user ID for {user_email}")
        return
    
    from core.conversation_manager import ConversationManager
    conv_mgr = ConversationManager(DB_PATH)
    conv_mgr.save_conversation(user_id, message, response, subject)


def get_conversation_history(user_email, limit=50):
    """Retrieve conversation history for a user"""
    user_id = get_user_id_by_email(user_email)
    if not user_id:
        return []
    
    from core.conversation_manager import ConversationManager
    conv_mgr = ConversationManager(DB_PATH)
    conversations = conv_mgr.get_user_conversations(user_id, limit)
    
    # Convert to old format for backward compatibility
    return [(c['question'], c['answer'], c['timestamp'], c['subject']) 
            for c in conversations]


def get_monthly_usage(user_email):
    """Get user's message count for current month"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    user_id = get_user_id_by_email(user_email)
    if not user_id:
        return 0
    
    current_month = datetime.now().strftime('%Y-%m')
    c.execute('''SELECT COUNT(*) FROM conversations 
                 WHERE user_id = ? 
                 AND strftime('%Y-%m', timestamp) = ?''',
              (user_id, current_month))
    
    count = c.fetchone()[0]
    conn.close()
    return count


def check_subscription_status(user_email):
    """Check if user has paid subscription"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT subscription_status FROM users WHERE email = ?', (user_email,))
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else 'free'


def upgrade_to_paid(user_email, stripe_customer_id=None):
    """Upgrade user to paid subscription"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''UPDATE users 
                 SET subscription_status = 'paid',
                     subscription_start_date = ?,
                     stripe_customer_id = ?
                 WHERE email = ?''',
              (datetime.now(), stripe_customer_id, user_email))
    
    conn.commit()
    conn.close()
    print(f"✅ User upgraded to paid: {user_email}")


def link_child(parent_email, child_email, child_name):
    """Link a child account to a parent"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''INSERT INTO children (parent_email, child_email, child_name)
                 VALUES (?, ?, ?)''', (parent_email, child_email, child_name))
    
    conn.commit()
    conn.close()


def get_children(parent_email):
    """Get all children linked to a parent"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT child_email, child_name FROM children 
                 WHERE parent_email = ?''', (parent_email,))
    
    children = c.fetchall()
    conn.close()
    return children


# API Usage tracking functions

def log_api_call(user_email, input_tokens, output_tokens, estimated_cost, model='claude-3-opus'):
    """Log API usage to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''INSERT INTO api_usage 
                 (user_email, input_tokens, output_tokens, estimated_cost, timestamp, model)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_email, input_tokens, output_tokens, estimated_cost, datetime.now(), model))
    
    conn.commit()
    conn.close()


def get_monthly_cost(user_email):
    """Get user's total API cost for current month"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    current_month = datetime.now().strftime('%Y-%m')
    c.execute('''SELECT COALESCE(SUM(estimated_cost), 0) as total_cost
                 FROM api_usage 
                 WHERE user_email = ? 
                 AND strftime('%Y-%m', timestamp) = ?''',
              (user_email, current_month))
    
    cost = c.fetchone()[0]
    conn.close()
    return cost


def get_all_users_stats():
    """Get statistics for all users (admin dashboard)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Total users by subscription type
    c.execute('''SELECT subscription_status, COUNT(*) as count 
                 FROM users 
                 GROUP BY subscription_status''')
    user_stats = c.fetchall()
    
    conn.close()
    return dict(user_stats)


def get_monthly_api_costs():
    """Get total API costs for current month (admin dashboard)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    current_month = datetime.now().strftime('%Y-%m')
    c.execute('''SELECT 
                     COUNT(*) as total_calls,
                     SUM(input_tokens) as total_input_tokens,
                     SUM(output_tokens) as total_output_tokens,
                     SUM(estimated_cost) as total_cost,
                     AVG(estimated_cost) as avg_cost_per_call
                 FROM api_usage
                 WHERE strftime('%Y-%m', timestamp) = ?''',
              (current_month,))
    
    stats = c.fetchone()
    conn.close()
    
    return {
        'total_calls': stats[0] or 0,
        'total_input_tokens': stats[1] or 0,
        'total_output_tokens': stats[2] or 0,
        'total_cost': stats[3] or 0,
        'avg_cost_per_call': stats[4] or 0
    }


def get_top_users_by_cost(limit=10):
    """Get top users by API cost (admin dashboard)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    current_month = datetime.now().strftime('%Y-%m')
    c.execute('''SELECT 
                     u.email,
                     u.name,
                     u.subscription_status,
                     COUNT(a.id) as total_calls,
                     SUM(a.estimated_cost) as total_cost
                 FROM users u
                 LEFT JOIN api_usage a ON u.email = a.user_email
                 WHERE strftime('%Y-%m', a.timestamp) = ?
                 GROUP BY u.email
                 ORDER BY total_cost DESC
                 LIMIT ?''',
              (current_month, limit))
    
    top_users = c.fetchall()
    conn.close()
    return top_users


def get_recent_api_calls(limit=20):
    """Get recent API calls (admin dashboard)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT 
                     user_email,
                     input_tokens,
                     output_tokens,
                     estimated_cost,
                     timestamp,
                     model
                 FROM api_usage
                 ORDER BY timestamp DESC
                 LIMIT ?''', (limit,))
    
    recent = c.fetchall()
    conn.close()
    return recent


def get_user_subscription_status(email):
    """Get user's current subscription status"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT subscription_status FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return None


if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
    print("\n🎉 Database setup complete!")
    print("Tables created: users, conversations, children, api_usage")