import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class ConversationManager:
    """Manages user conversation history"""
    
    def __init__(self, db_path: str = 'educapp_users.db'):
        self.db_path = db_path
        self._ensure_title_column()
    
    def _ensure_title_column(self):
        """Ensure the title column exists in conversations table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if title column exists
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'title' not in columns:
                cursor.execute('ALTER TABLE conversations ADD COLUMN title TEXT')
                conn.commit()
                print("✅ Added 'title' column to conversations table")
            
            conn.close()
            
        except Exception as e:
            print(f"Error ensuring title column: {e}")
    
    def save_conversation(self, user_id: int, question: str, answer: str, subject: str = None) -> bool:
        """Save a conversation to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO conversations (user_id, question, answer, subject, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, question, answer, subject, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def get_user_conversations(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get conversation history for a user (includes title)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if title column exists
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'title' in columns:
                cursor.execute('''
                SELECT id, question, answer, subject, timestamp, title
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                ''', (user_id, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        'id': row[0],
                        'question': row[1],
                        'answer': row[2],
                        'subject': row[3],
                        'timestamp': row[4],
                        'title': row[5]
                    })
            else:
                # Fallback if title column doesn't exist yet
                cursor.execute('''
                SELECT id, question, answer, subject, timestamp
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                ''', (user_id, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        'id': row[0],
                        'question': row[1],
                        'answer': row[2],
                        'subject': row[3],
                        'timestamp': row[4],
                        'title': None
                    })
            
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def get_conversation_count(self, user_id: int) -> int:
        """Get total number of conversations for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT COUNT(*) FROM conversations WHERE user_id = ?
            ''', (user_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error getting conversation count: {e}")
            return 0
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a specific conversation (only if it belongs to the user)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM conversations 
            WHERE id = ? AND user_id = ?
            ''', (conversation_id, user_id))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
            
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def clear_user_history(self, user_id: int) -> bool:
        """Clear all conversations for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM conversations WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
    
    def update_conversation_title(self, conversation_id: int, title: str, user_id: int) -> bool:
        """Update the title of a conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update the title (only if conversation belongs to user)
            cursor.execute('''
            UPDATE conversations 
            SET title = ?
            WHERE id = ? AND user_id = ?
            ''', (title, conversation_id, user_id))
            
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
            
        except Exception as e:
            print(f"Error updating conversation title: {e}")
            return False