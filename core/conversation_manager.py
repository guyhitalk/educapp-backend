"""
Conversation Manager for EducApp
Handles saving, retrieving, and managing user conversations
"""

from core.database_supabase import SupabaseDatabase
from datetime import datetime

class ConversationManager:
    def __init__(self):
        self.db = SupabaseDatabase()
    
    def save_conversation(self, user_id, question, answer, subject=None):
        """Save a conversation to database"""
        try:
            self.db.save_conversation(user_id, question, answer)
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def get_user_conversations(self, user_id, limit=50):
        """Get user's conversation history"""
        try:
            conversations = self.db.get_user_conversations(user_id, limit)
            
            # Format conversations for display
            formatted = []
            for conv in conversations:
                formatted.append({
                    'id': conv['id'],
                    'question': conv['question'],
                    'answer': conv['answer'],
                    'timestamp': conv['timestamp'],
                    'subject': 'General',  # Add subject detection if needed
                    'title': None  # Custom titles not yet implemented
                })
            
            return formatted
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return []
    
    def delete_conversation(self, conversation_id, user_id):
        """Delete a specific conversation"""
        try:
            self.db.delete_conversation(conversation_id, user_id)
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def clear_user_history(self, user_id):
        """Clear all conversations for a user"""
        try:
            self.db.clear_user_conversations(user_id)
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
    
    def update_conversation_title(self, conversation_id, title, user_id):
        """Update conversation title (not yet implemented in database)"""
        # TODO: Add title column to database and implement
        return False