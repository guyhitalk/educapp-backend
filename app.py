"""
EducApp - Faith-Driven AI Tutor Interface
Streamlit web application for Christian Education
"""

import streamlit as st
from core.chatbot import EducAppTutor
from core.auth import check_authentication, logout, get_current_user
from core.freemium import get_user_usage, can_ask_question, increment_question_count, get_upgrade_message
from core.conversation_manager import ConversationManager
from core.database_supabase import SupabaseDatabase
import sys
from datetime import datetime

# Initialize database
@st.cache_resource
def get_database():
    """Get database instance - cached to reuse connection"""
    return SupabaseDatabase()

# Helper function to get user ID by email
def get_user_id_by_email(email):
    """Get user ID from email"""
    db = get_database()
    user = db.get_user_by_email(email)
    return user['id'] if user else None

# Page configuration
st.set_page_config(
    page_title="EducApp - Christian AI Tutor",
    page_icon="✝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize chatbot (cached to avoid reloading)
@st.cache_resource
def load_tutor():
    """Load the AI tutor - this only runs once"""
    try:
        return EducAppTutor()
    except Exception as e:
        st.error(f"Error initializing tutor: {e}")
        return None

# Initialize conversation manager (cached)
@st.cache_resource
def load_conversation_manager():
    """Load conversation manager - this only runs once"""
    return ConversationManager()

def show_conversation_history():
    """Display user's conversation history with search and rename"""
    st.title("📚 Conversation History")
    
    current_user = get_current_user()
    user_email = current_user['email']
    user_id = get_user_id_by_email(user_email)
    
    if not user_id:
        st.error("Could not load your conversation history.")
        return
    
    conv_mgr = load_conversation_manager()
    conversations = conv_mgr.get_user_conversations(user_id, limit=100)
    
    if not conversations:
        st.info("📝 No conversations yet. Start asking questions!")
        return
    
    # Search box
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search conversations", placeholder="Enter keyword to filter...")
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🗑️ Clear All History"):
            if st.session_state.get('confirm_clear', False):
                conv_mgr.clear_user_history(user_id)
                st.success("History cleared!")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm deletion of ALL conversations")
    
    # Filter conversations by search query
    filtered_conversations = conversations
    if search_query:
        search_lower = search_query.lower()
        filtered_conversations = [
            conv for conv in conversations 
            if search_lower in conv['question'].lower() 
            or search_lower in conv['answer'].lower()
            or (conv['subject'] and search_lower in conv['subject'].lower())
            or (conv.get('title') and search_lower in conv['title'].lower())
        ]
    
    # Display results
    st.write(f"**Showing {len(filtered_conversations)} of {len(conversations)} conversations**")
    
    if search_query and not filtered_conversations:
        st.warning(f"No conversations found matching '{search_query}'")
        return
    
    st.markdown("---")
    
    # Display conversations
    for i, conv in enumerate(filtered_conversations, 1):
        timestamp = conv['timestamp']
        subject = conv['subject'] or "General"
        conv_id = conv['id']
        
        # Get display title - ensure it's never None or empty
        custom_title = conv.get('title')
        if custom_title:
            display_title = custom_title
        else:
            display_title = f"#{conv_id} - {subject} - {timestamp}"
        
        with st.expander(display_title, expanded=(i==1)):
            # Rename section
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_title = st.text_input(
                    "✏️ Rename conversation", 
                    value=custom_title if custom_title else '',
                    placeholder=f"e.g., 'Technology Discussion'",
                    key=f"title_{conv_id}"
                )
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("💾 Save", key=f"save_title_{conv_id}"):
                    if conv_mgr.update_conversation_title(conv_id, new_title if new_title else None, user_id):
                        st.success("Title updated!")
                        st.rerun()
                    else:
                        st.error("Failed to update title")
            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("🔄 Reset", key=f"reset_title_{conv_id}"):
                    if conv_mgr.update_conversation_title(conv_id, None, user_id):
                        st.success("Title reset!")
                        st.rerun()
            
            st.markdown("---")
            st.markdown(f"**📅 Date:** {timestamp}")
            st.markdown(f"**📚 Subject:** {subject}")
            st.markdown("---")
            
            # Question section
            st.markdown("**❓ Question:**")
            st.info(conv['question'])
            
            st.markdown("---")
            
            # Answer section
            st.markdown("**✅ Answer:**")
            st.success(conv['answer'])
            
            # Delete button
            st.markdown("---")
            if st.button(f"🗑️ Delete this conversation", key=f"delete_{conv_id}"):
                if conv_mgr.delete_conversation(conv_id, user_id):
                    st.success("Conversation deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete conversation.")

def main():
    # Check authentication first
    check_authentication()
    
    # Get current user
    current_user = get_current_user()
    user_email = current_user['email']
    user_name = current_user['name']
    
    # Sidebar configuration
    with st.sidebar:
        # Navigation
        page = st.radio(
            "📍 Navigation",
            ["🏠 Chat", "📚 History"],
            label_visibility="visible"
        )
        
        st.markdown("---")
        
        # Show user info
        st.write(f"**Welcome, {user_name}!**")
        st.caption(user_email)
        
        # Show usage for free users
        usage = get_user_usage(user_email)
        if usage and usage['has_limit']:
            questions_left = usage['limit'] - usage['questions_used']
            if questions_left > 0:
                st.info(f"📊 **{usage['questions_used']}/{usage['limit']}** questions used this month")
            else:
                st.warning(f"⚠️ **{usage['limit']}/{usage['limit']}** questions used - Upgrade for unlimited!")
        elif usage and usage['status'] == 'paid':
            st.success("✅ **Premium Member** - Unlimited questions!")
        
        if st.button("🚪 Logout"):
            logout()
        
        st.markdown("---")
        
        # Biblical Foundation
        st.header("Biblical Foundation")
        st.info("EducApp integrates biblical principles across all subjects. The Bible is true and authoritative. Jesus is the Way, the Truth, and the Life.")
        
        if st.button("View Worldview Statement"):
            from config.worldview_foundation import WORLDVIEW_STATEMENT
            st.text_area("Biblical Worldview", WORLDVIEW_STATEMENT, height=300)
        
        st.markdown("---")
        if st.button("🔄 Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Route to appropriate page
    if page == "📚 History":
        show_conversation_history()
        return
    
    # Main Chat Page
    st.title("EducApp ✝")
    st.markdown("*Faith-Driven AI Tutor for Christian Education*")
    st.markdown("*An EdTech platform with a Christian worldview, with its principles and values biblically based*")
    st.markdown("---")
    
    # Load tutor and conversation manager
    tutor = load_tutor()
    conv_mgr = load_conversation_manager()
    
    if tutor is None:
        st.error("Failed to initialize AI tutor. Please check your setup and try again.")
        return
    
    # Get user ID for conversation saving
    user_id = get_user_id_by_email(user_email)
    
    # Initialize conversation history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Hidden settings - AI uses all subjects and adapts automatically
    student_name = user_name
    grade = None  # AI will adapt to question level
    subject = "General"  # AI will detect subject from question
    
    # User input
    if prompt := st.chat_input(f"Ask your question, {user_name}..."):
        # Check if user can ask questions
        if not can_ask_question(user_email):
            from core.stripe_payment import check_payment_success
            
            st.error("⚠️ You've reached your monthly question limit!")
            
            # Check if returning from successful payment
            payment_result = check_payment_success()
            
            # Show upgrade message with payment button
            upgrade_message, checkout_url = get_upgrade_message(user_email, user_name)
            st.markdown(upgrade_message)
            
            if checkout_url:
                st.link_button("💳 Upgrade to Premium - $19/month", checkout_url, type="primary", use_container_width=True)
            else:
                st.info("**To upgrade, contact:** guy@hitalk.us")
            
            st.stop()
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🙏 Thinking biblically..."):
                try:
                    response = tutor.get_response(
                        student_question=prompt,
                        subject=subject,
                        student_grade=grade,
                        user_email=user_email
                    )
                    st.markdown(response)
                    
                    # Save conversation to database
                    if user_id:
                        conv_mgr.save_conversation(
                            user_id=user_id,
                            question=prompt,
                            answer=response,
                            subject=subject
                        )
                    
                    # Increment question counter AFTER successful response
                    increment_question_count(user_email)
                    
                except Exception as e:
                    error_msg = f"I encountered an error. Please try again. Error: {str(e)}"
                    st.error(error_msg)
                    response = error_msg
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Footer
    st.markdown("---")
    st.caption("EducApp empowers parents as primary educators. Always discuss important questions with your family and church.")
    st.caption("The Bible is God's inspired, inerrant, authoritative Word. Jesus is the Way, the Truth, and the Life.")

if __name__ == "__main__":
    main()