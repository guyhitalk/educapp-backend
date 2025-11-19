# core/stripe_payment.py
"""
Stripe payment integration for EducApp
"""

import stripe
import os
from dotenv import load_dotenv
from core.database import upgrade_to_paid

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')


def create_checkout_session(user_email, user_name):
    """
    Create a Stripe checkout session for subscription
    Returns the checkout URL
    """
    try:
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=user_email,
            line_items=[
                {
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url='http://localhost:8501/?success=true',
            cancel_url='http://localhost:8501/?canceled=true',
            metadata={
                'user_email': user_email,
                'user_name': user_name,
            }
        )
        
        return checkout_session.url
        
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return None


def get_stripe_checkout_url(user_email, user_name):
    """
    Get Stripe checkout URL (returns URL string, not HTML)
    """
    return create_checkout_session(user_email, user_name)


def verify_payment(session_id):
    """
    Verify a payment was successful and upgrade user
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Get user email from metadata
            user_email = session.metadata.get('user_email')
            
            if user_email:
                # Upgrade user to paid
                upgrade_to_paid(user_email)
                return True
        
        return False
        
    except Exception as e:
        print(f"Error verifying payment: {e}")
        return False


def check_payment_success():
    """
    Check if payment was successful from URL parameter
    This is called when user returns from Stripe checkout
    """
    import streamlit as st
    
    # Check URL parameters
    query_params = st.query_params
    
    if 'success' in query_params:
        # Payment completed - user came back from Stripe
        # Get current user email
        from core.auth import get_current_user
        current_user = get_current_user()
        user_email = current_user['email']
        
        # Check if user needs to be upgraded
        from core.database import get_user_subscription_status
        current_status = get_user_subscription_status(user_email)
        
        if current_status != 'paid':
            # Upgrade the user
            from core.database import upgrade_to_paid
            upgrade_to_paid(user_email)
            st.success("🎉 Payment successful! Your account has been upgraded to Premium!")
            st.balloons()
            # Clear the URL parameter
            st.query_params.clear()
            # Force reload to update sidebar
            st.rerun()
        else:
            st.success("✅ You're already a Premium member!")
        
        return True
    
    if 'canceled' in query_params:
        st.warning("⚠️ Payment was canceled. You can try again anytime!")
        # Clear the URL parameter
        st.query_params.clear()
        return False
    
    return None