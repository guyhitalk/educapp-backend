# core/freemium.py
"""
Freemium limits and upgrade management for EducApp
"""

import sqlite3
from datetime import datetime
from core.database import DB_PATH

# Freemium settings
FREE_MONTHLY_LIMIT = 10
PAID_MONTHLY_PRICE = 19  # USD


def get_user_usage(email):
    """Get user's current usage and subscription status"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT subscription_status, questions_this_month, last_reset_date 
                 FROM users WHERE email = ?''', (email,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return None
    
    status, questions_count, last_reset = result
    
    # Check if we need to reset the counter (new month)
    if last_reset:
        last_reset_date = datetime.strptime(last_reset, '%Y-%m-%d')
        now = datetime.now()
        
        # If it's a new month, reset counter
        if now.month != last_reset_date.month or now.year != last_reset_date.year:
            reset_monthly_counter(email)
            questions_count = 0
    
    return {
        'status': status,
        'questions_used': questions_count or 0,
        'limit': FREE_MONTHLY_LIMIT if status == 'free' else None,
        'has_limit': status == 'free',
        'is_at_limit': (status == 'free' and (questions_count or 0) >= FREE_MONTHLY_LIMIT)
    }


def reset_monthly_counter(email):
    """Reset monthly question counter for a user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''UPDATE users 
                 SET questions_this_month = 0,
                     last_reset_date = ?
                 WHERE email = ?''',
              (datetime.now().strftime('%Y-%m-%d'), email))
    
    conn.commit()
    conn.close()
    print(f"🔄 Reset monthly counter for {email}")


def increment_question_count(email):
    """Increment user's question count"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''UPDATE users 
                 SET questions_this_month = questions_this_month + 1
                 WHERE email = ?''', (email,))
    
    conn.commit()
    conn.close()


def can_ask_question(email):
    """Check if user can ask another question"""
    usage = get_user_usage(email)
    
    if not usage:
        return False
    
    # Paid users can always ask
    if usage['status'] == 'paid':
        return True
    
    # Free users check limit
    return usage['questions_used'] < FREE_MONTHLY_LIMIT


def get_upgrade_message(user_email, user_name):
    """Get the upgrade prompt message with Stripe checkout URL"""
    from core.stripe_payment import get_stripe_checkout_url
    
    # Get Stripe checkout URL
    checkout_url = get_stripe_checkout_url(user_email, user_name)
    
    message = f"""
### 🎓 Upgrade to EducApp Premium

You've reached your free limit of **{FREE_MONTHLY_LIMIT} questions** this month.

**Upgrade to Premium for:**
- ✅ **Unlimited questions** every month
- ✅ Full access to all subjects
- ✅ Priority support
- ✅ Support Christian education

**Only $19/month**

*Your monthly question limit resets on the 1st of each month.*
"""
    
    return message, checkout_url