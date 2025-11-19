"""
Google OAuth Authentication for EducApp
"""
import os
import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
from core.database import user_exists, create_user, get_user
import secrets

def get_google_client_id():
    """Get Google OAuth client ID from environment"""
    return os.getenv('GOOGLE_CLIENT_ID')

def get_google_client_secret():
    """Get Google OAuth client secret from environment"""
    return os.getenv('GOOGLE_CLIENT_SECRET')

def init_google_auth():
    """Initialize Google OAuth in session state"""
    if 'google_auth_initialized' not in st.session_state:
        st.session_state.google_auth_initialized = True
        st.session_state.google_user_info = None

def show_google_login_button():
    """Display Google Sign-In button using HTML/JavaScript"""
    client_id = get_google_client_id()
    
    if not client_id:
        st.error("Google OAuth not configured. Please add GOOGLE_CLIENT_ID to .env file.")
        return
    
    # Google Sign-In HTML with JavaScript
    google_login_html = f"""
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <div id="g_id_onload"
         data-client_id="{client_id}"
         data-callback="handleCredentialResponse"
         data-auto_prompt="false">
    </div>
    <div class="g_id_signin"
         data-type="standard"
         data-size="large"
         data-theme="outline"
         data-text="sign_in_with"
         data-shape="rectangular"
         data-logo_alignment="left">
    </div>
    
    <script>
    function handleCredentialResponse(response) {{
        // Send the credential to Streamlit
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            data: response.credential
        }}, '*');
    }}
    </script>
    """
    
    st.components.v1.html(google_login_html, height=50)

def verify_google_token(token):
    """Verify Google ID token and return user info"""
    try:
        client_id = get_google_client_id()
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            client_id
        )
        
        # Token is valid, return user info
        return {
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'email_verified': idinfo.get('email_verified', False)
        }
        
    except Exception as e:
        st.error(f"Token verification failed: {e}")
        return None

def handle_google_login(user_info):
    """Handle user login after Google authentication"""
    email = user_info['email']
    name = user_info['name']
    
    # Check if user exists
    if not user_exists(email):
        # Create new user with random password (they'll use Google to login)
        random_password = secrets.token_urlsafe(32)
        create_user(email, name, random_password)
        st.success(f"Welcome to EducApp, {name}!")
    else:
        st.success(f"Welcome back, {name}!")
    
    # Set session state
    st.session_state.authenticated = True
    st.session_state.user_email = email
    st.session_state.user_name = name
    
    # Force reload to show main app
    st.rerun()