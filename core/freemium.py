"""
Freemium system for EducApp
Manages question limits and subscription status
"""

import streamlit as st
from datetime import datetime, date
from core.database_supabase import SupabaseDatabase

# Initialize database
db = SupabaseDatabase()

# Free tier limits
FREE_QUESTIONS_PER_MONTH = 10

def get_user_usage(email):
    """Get user's current usage and limits"""
    user = db.get_user_by_email(email)
    
    if not user:
        return None
    
    # Check if user is paid
    if user.get('subscription_status') == 'active':
        return {
            'status': 'paid',
            'has_limit': False,
            'questions_used': user.get('questions_asked', 0),
            'limit': None
        }
    
    # Free user - check if monthly reset is needed
    last_reset = user.get('last_reset_date')
    today = date.today()
    
    if last_reset:
        # Convert string to date if needed
        if isinstance(last_reset, str):
            last_reset = datetime.strptime(last_reset, '%Y-%m-%d').date()
        
        # Reset if it's a new month
        if last_reset.month != today.month or last_reset.year != today.year:
            db.reset_monthly_questions(user['id'])
            questions_used = 0
        else:
            questions_used = user.get('questions_asked', 0)
    else:
        questions_used = user.get('questions_asked', 0)
    
    return {
        'status': 'free',
        'has_limit': True,
        'questions_used': questions_used,
        'limit': FREE_QUESTIONS_PER_MONTH
    }

def can_ask_question(email):
    """Check if user can ask a question"""
    usage = get_user_usage(email)
    
    if not usage:
        return False
    
    # Paid users can always ask
    if usage['status'] == 'paid':
        return True
    
    # Free users check limit
    return usage['questions_used'] < usage['limit']

def increment_question_count(email):
    """Increment user's question count"""
    user = db.get_user_by_email(email)
    
    if user:
        db.increment_questions_asked(user['id'])

def get_upgrade_message(email, name):
    """Get upgrade message for user"""
    from core.stripe_payment import create_checkout_session
    
    # Try to create checkout session
    checkout_url = create_checkout_session(email, name)
    
    message = f"""
    ### 🎯 Upgrade to Premium - Unlimited Access!
    
    **Premium Benefits:**
    - ✅ Unlimited questions every month
    - ✅ Priority support
    - ✅ Access to all subjects
    - ✅ Conversation history (unlimited)
    - ✅ Support Christian education development
    
    **Only $15/month** - Cancel anytime
    """
    
    return message, checkout_url