# core/auth.py
"""
Authentication for EducApp - Email/Password + Google OAuth
"""

import streamlit as st
from core.database import create_user, verify_password, user_exists, get_user
import os

def show_login_page():
    """Display login/signup page with Google OAuth option"""
    
    st.title("EducApp ✝")
    st.markdown("*Faith-Driven AI Tutor for Christian Education*")
    st.markdown("---")
    
    # Google Sign-In Section
    st.subheader("🚀 Quick Sign In")
    
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    
    if client_id:
        st.info("👉 **Use Google Sign-In for fastest access!**")
        show_google_signin_simple(client_id)
    else:
        st.warning("⚠️ Google Sign-In not configured")
    
    st.markdown("---")
    st.markdown("**Or use email/password:**")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()


def show_google_signin_simple(client_id):
    """Simplified Google Sign-In using direct HTML button"""
    
    # Simple HTML form that redirects to Google OAuth
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri=http://localhost:8501&response_type=code&scope=openid%20email%20profile&access_type=offline"
    
    # Check if we have an authorization code in the URL
    query_params = st.query_params
    
    if 'code' in query_params:
        auth_code = query_params['code']
        handle_google_oauth_code(auth_code)
        return
    
    # Display button that opens Google login
    st.markdown(
        f"""
        <a href="{google_auth_url}" target="_self">
            <button style="
                background-color: white;
                color: #444;
                border: 1px solid #ddd;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 4px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                font-family: Arial, sans-serif;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <img src="https://www.google.com/favicon.ico" width="20" height="20">
                Sign in with Google
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )


def handle_google_oauth_code(code):
    """Exchange authorization code for user info"""
    try:
        import requests
        import secrets
        
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': 'http://localhost:8501',
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            st.error("❌ Failed to get access token from Google")
            st.query_params.clear()
            return
        
        access_token = token_json['access_token']
        
        # Get user info
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        user_info = user_info_response.json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        verified = user_info.get('verified_email', False)
        
        if not verified:
            st.error("❌ Email not verified with Google")
            st.query_params.clear()
            return
        
        # Check if user exists
        if not user_exists(email):
            # Create new user with random password
            random_password = secrets.token_urlsafe(32)
            create_user(email, name, random_password)
            st.success(f"✅ Welcome to EducApp, {name}!")
        else:
            st.success(f"✅ Welcome back, {name}!")
        
        # Set session state
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.user_name = name
        st.session_state.auth_method = 'google'
        
        # Clear query params and reload
        st.query_params.clear()
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Google Sign-In failed: {str(e)}")
        st.query_params.clear()


def show_login_form():
    """Login form"""
    st.subheader("Welcome Back!")
    
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
                return
            
            if verify_password(email, password):
                # Get user info
                user_info = get_user(email)
                if user_info:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = user_info[1]  # name is second column
                    st.session_state.auth_method = 'email'
                    st.success("✅ Login successful!")
                    st.rerun()
            else:
                st.error("❌ Invalid email or password")


def show_signup_form():
    """Signup form with Terms of Service"""
    st.subheader("Create Your Account")
    
    # Show Terms of Service in expander
    with st.expander("📋 Terms of Service (Click to read)", expanded=False):
        from config.terms_of_service import TERMS_OF_SERVICE
        st.markdown(TERMS_OF_SERVICE)
    
    with st.form("signup_form"):
        name = st.text_input("Your Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="signup_password_confirm")
        
        st.markdown("---")
        agree = st.checkbox("I have read and agree to the Terms of Service above, and agree to use EducApp in accordance with biblical values and parental oversight")
        
        submit = st.form_submit_button("Create Account")
        
        if submit:
            # Validation
            if not name or not email or not password:
                st.error("Please fill in all fields")
                return
            
            if not agree:
                st.error("Please read and agree to the Terms of Service")
                return
            
            if password != password_confirm:
                st.error("Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return
            
            if user_exists(email):
                st.error("Email already registered. Please login.")
                return
            
            # Create user
            if create_user(email, name, password):
                st.success("✅ Account created! Please login.")
                st.balloons()
            else:
                st.error("Error creating account. Please try again.")


def check_authentication():
    """Check if user is authenticated"""
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        st.stop()


def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.auth_method = None
    st.rerun()


def get_current_user():
    """Get current logged-in user info"""
    if st.session_state.get('authenticated'):
        return {
            'email': st.session_state.get('user_email'),
            'name': st.session_state.get('user_name'),
            'auth_method': st.session_state.get('auth_method', 'email')
        }
    return None