"""
Supabase Database Handler for EducApp
Uses Supabase REST API instead of direct PostgreSQL
"""

import os
from supabase import create_client, Client
from datetime import datetime
import bcrypt
from dotenv import load_dotenv

load_dotenv()

class SupabaseDatabase:
    def __init__(self):
        # Use Supabase REST API
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.client: Client = create_client(self.url, self.key)
        # Note: Table creation should be done via Supabase Dashboard SQL editor
    
    # USER MANAGEMENT
    def create_user(self, email, password=None, name=None, google_id=None):
        """Create new user"""
        password_hash = None
        if password:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            data = {
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'google_id': google_id,
                'last_reset_date': datetime.now().date().isoformat(),
                'questions_asked': 0,
                'subscription_status': 'free'
            }
            
            response = self.client.table('users').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]['id']
            return None
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_google_id(self, google_id):
        """Get user by Google ID"""
        try:
            response = self.client.table('users').select('*').eq('google_id', google_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error getting user by Google ID: {e}")
            return None
    
    def verify_password(self, email, password):
        """Verify user password"""
        user = self.get_user_by_email(email)
        if not user or not user.get('password_hash'):
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
        except:
            return False
    
    def update_subscription(self, email, status, subscription_id=None):
        """Update user subscription"""
        try:
            data = {
                'subscription_status': status,
                'subscription_id': subscription_id
            }
            
            self.client.table('users').update(data).eq('email', email).execute()
            
        except Exception as e:
            print(f"Error updating subscription: {e}")
    
    # CONVERSATION MANAGEMENT
    def save_conversation(self, user_id, question, answer):
        """Save conversation"""
        try:
            data = {
                'user_id': user_id,
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            }
            
            self.client.table('conversations').insert(data).execute()
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def get_user_conversations(self, user_id, limit=50):
        """Get user conversations"""
        try:
            response = self.client.table('conversations')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def delete_conversation(self, conversation_id, user_id):
        """Delete specific conversation"""
        try:
            self.client.table('conversations')\
                .delete()\
                .eq('id', conversation_id)\
                .eq('user_id', user_id)\
                .execute()
                
        except Exception as e:
            print(f"Error deleting conversation: {e}")
    
    def clear_user_conversations(self, user_id):
        """Clear all conversations for user"""
        try:
            self.client.table('conversations')\
                .delete()\
                .eq('user_id', user_id)\
                .execute()
                
        except Exception as e:
            print(f"Error clearing conversations: {e}")
    
    # USAGE TRACKING
    def increment_questions_asked(self, user_id):
        """Increment question count"""
        try:
            # Get current count
            user_response = self.client.table('users').select('questions_asked').eq('id', user_id).execute()
            
            if user_response.data and len(user_response.data) > 0:
                current_count = user_response.data[0].get('questions_asked', 0)
                new_count = current_count + 1
                
                # Update count
                self.client.table('users').update({'questions_asked': new_count}).eq('id', user_id).execute()
                
        except Exception as e:
            print(f"Error incrementing questions: {e}")
    
    def reset_monthly_questions(self, user_id):
        """Reset monthly question count"""
        try:
            data = {
                'questions_asked': 0,
                'last_reset_date': datetime.now().date().isoformat()
            }
            
            self.client.table('users').update(data).eq('id', user_id).execute()
            
        except Exception as e:
            print(f"Error resetting questions: {e}")
    
    # ADMIN FUNCTIONS
    def get_all_users(self):
        """Get all users (admin)"""
        try:
            response = self.client.table('users')\
                .select('*')\
                .order('created_at', desc=True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_user_stats(self):
        """Get user statistics"""
        try:
            # Get all users
            response = self.client.table('users').select('subscription_status, questions_asked').execute()
            
            if not response.data:
                return {
                    'total_users': 0,
                    'paid_users': 0,
                    'free_users': 0,
                    'total_questions': 0
                }
            
            users = response.data
            
            stats = {
                'total_users': len(users),
                'paid_users': sum(1 for u in users if u.get('subscription_status') == 'active'),
                'free_users': sum(1 for u in users if u.get('subscription_status') == 'free'),
                'total_questions': sum(u.get('questions_asked', 0) for u in users)
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                'total_users': 0,
                'paid_users': 0,
                'free_users': 0,
                'total_questions': 0
            }