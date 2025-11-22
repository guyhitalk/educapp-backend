"""
Authentication system for EducApp
Handles user login, signup, and session management
"""

import streamlit as st
from core.database_supabase import SupabaseDatabase
import bcrypt

# Initialize database
db = SupabaseDatabase()

def create_user(email, password=None, name=None, google_id=None):
    """Create new user"""
    return db.create_user(email, password, name, google_id)

def verify_password(email, password):
    """Verify user password"""
    return db.verify_password(email, password)

def user_exists(email):
    """Check if user exists"""
    user = db.get_user_by_email(email)
    return user is not None

def get_user(email):
    """Get user by email"""
    return db.get_user_by_email(email)

def show_login_form():
    """Display login form"""
    st.title("EducApp ✝")
    st.markdown("### Faith-Driven AI Tutor for Christian Education")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["�� Login", "📝 Sign Up", "🔑 Google Sign-In"])
    
    # Login Tab
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password")
                elif verify_password(email, password):
                    user = get_user(email)
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = user.get('name', email.split('@')[0])
                    st.session_state.user_id = user.get('id')
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
    
    # Sign Up Tab
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
            agree = st.checkbox("I agree to the Terms of Service")
            submit = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submit:
                if not all([name, email, password, password_confirm]):
                    st.error("Please fill in all fields")
                elif password != password_confirm:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                elif not agree:
                    st.error("Please agree to the Terms of Service")
                elif user_exists(email):
                    st.error("Email already registered. Please login.")
                else:
                    user_id = create_user(email, password, name)
                    if user_id:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = name
                        st.session_state.user_id = user_id
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create account. Please try again.")
        
        if st.button("View Terms of Service"):
            from config.terms_of_service import TERMS_OF_SERVICE
            st.text_area("Terms of Service", TERMS_OF_SERVICE, height=300)
    
    # Google Sign-In Tab
    with tab3:
        st.subheader("Sign in with Google")
        st.info("🚧 Google Sign-In will be available soon!")
        st.markdown("For now, please use email/password to create an account.")
        
        # TODO: Implement Google OAuth when custom domain is ready

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        show_login_form()
        st.stop()

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_id = None
    st.rerun()

def get_current_user():
    """Get current logged-in user info"""
    return {
        'email': st.session_state.get('user_email'),
        'name': st.session_state.get('user_name'),
        'id': st.session_state.get('user_id')
    }
