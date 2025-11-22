"""
Supabase Database Handler for EducApp
Replaces SQLite with PostgreSQL on Supabase
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import bcrypt
from dotenv import load_dotenv

load_dotenv()

class SupabaseDatabase:
    def __init__(self):
        self.connection_string = os.getenv('SUPABASE_URL')
        self._create_tables()
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)
    
    def _create_tables(self):
        """Create all necessary tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                name TEXT,
                google_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subscription_status TEXT DEFAULT 'free',
                subscription_id TEXT,
                questions_asked INTEGER DEFAULT 0,
                last_reset_date DATE
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    
    # USER MANAGEMENT
    def create_user(self, email, password=None, name=None, google_id=None):
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = None
        if password:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, name, google_id, last_reset_date)
                VALUES (%s, %s, %s, %s, CURRENT_DATE)
                RETURNING id
            ''', (email, password_hash, name, google_id))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
        except psycopg2.IntegrityError:
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return dict(user) if user else None
    
    def get_user_by_google_id(self, google_id):
        """Get user by Google ID"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT * FROM users WHERE google_id = %s', (google_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return dict(user) if user else None
    
    def verify_password(self, email, password):
        """Verify user password"""
        user = self.get_user_by_email(email)
        if not user or not user['password_hash']:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
    
    def update_subscription(self, email, status, subscription_id=None):
        """Update user subscription"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET subscription_status = %s, subscription_id = %s
            WHERE email = %s
        ''', (status, subscription_id, email))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    # CONVERSATION MANAGEMENT
    def save_conversation(self, user_id, question, answer):
        """Save conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_id, question, answer)
            VALUES (%s, %s, %s)
        ''', (user_id, question, answer))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_user_conversations(self, user_id, limit=50):
        """Get user conversations"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT * FROM conversations 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        ''', (user_id, limit))
        
        conversations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return [dict(conv) for conv in conversations]
    
    def delete_conversation(self, conversation_id, user_id):
        """Delete specific conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM conversations 
            WHERE id = %s AND user_id = %s
        ''', (conversation_id, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def clear_user_conversations(self, user_id):
        """Clear all conversations for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM conversations WHERE user_id = %s', (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    # USAGE TRACKING
    def increment_questions_asked(self, user_id):
        """Increment question count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET questions_asked = questions_asked + 1 
            WHERE id = %s
        ''', (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def reset_monthly_questions(self, user_id):
        """Reset monthly question count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET questions_asked = 0, last_reset_date = CURRENT_DATE
            WHERE id = %s
        ''', (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    # ADMIN FUNCTIONS
    def get_all_users(self):
        """Get all users (admin)"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return [dict(user) for user in users]
    
    def get_user_stats(self):
        """Get user statistics"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN subscription_status = 'active' THEN 1 END) as paid_users,
                COUNT(CASE WHEN subscription_status = 'free' THEN 1 END) as free_users,
                SUM(questions_asked) as total_questions
            FROM users
        ''')
        
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return dict(stats) if stats else {}

