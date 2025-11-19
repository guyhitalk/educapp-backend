# admin_users.py
"""
EducApp User Management Dashboard
View, search, and export user data
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# SECURITY: Use same password as main admin dashboard
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'educapp2024')

# Page config
st.set_page_config(
    page_title="EducApp User Management",
    page_icon="👥",
    layout="wide"
)

def check_password():
    """Password protection for admin dashboard"""
    
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.title("🔐 EducApp User Management")
        st.write("Enter admin password to continue")
        
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password")
        
        st.stop()


def show_user_dashboard():
    """Main user management dashboard"""
    
    st.title("👥 EducApp User Management")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    # === OVERVIEW METRICS ===
    st.header("📊 User Overview")
    
    conn = sqlite3.connect('educapp_users.db')
    cursor = conn.cursor()
    
    # Total users
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Free vs Paid
    cursor.execute('SELECT COUNT(*) FROM users WHERE subscription_status = "free"')
    free_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE subscription_status = "paid"')
    paid_users = cursor.fetchone()[0]
    
    # Total conversations
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cursor.fetchone()[0]
    
    # New users this month
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT COUNT(*) FROM users 
        WHERE strftime('%Y-%m', created_at) = ?
    ''', (current_month,))
    new_users_month = cursor.fetchone()[0]
    
    conn.close()
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("👥 Total Users", total_users)
    
    with col2:
        st.metric("🆓 Free Users", free_users)
    
    with col3:
        st.metric("💎 Paid Users", paid_users)
    
    with col4:
        st.metric("💬 Total Conversations", total_conversations)
    
    with col5:
        st.metric("🆕 New This Month", new_users_month)
    
    st.markdown("---")
    
    # === TABS ===
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 All Users", 
        "🔥 Most Active", 
        "🆕 Recent Signups", 
        "📤 Export Data"
    ])
    
    with tab1:
        show_all_users()
    
    with tab2:
        show_active_users()
    
    with tab3:
        show_recent_signups()
    
    with tab4:
        show_export_tools()


def show_all_users():
    """Display all registered users with search"""
    st.subheader("📋 All Registered Users")
    
    # Search box
    search_query = st.text_input("🔍 Search by name or email", placeholder="Type to search...")
    
    conn = sqlite3.connect('educapp_users.db')
    
    # Base query
    if search_query:
        query = '''
            SELECT 
                u.id,
                u.email,
                u.name,
                u.created_at,
                u.subscription_status,
                u.questions_this_month,
                COUNT(c.id) as total_conversations
            FROM users u
            LEFT JOIN conversations c ON u.id = c.user_id
            WHERE u.email LIKE ? OR u.name LIKE ?
            GROUP BY u.id
            ORDER BY u.created_at DESC
        '''
        search_pattern = f'%{search_query}%'
        df_users = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern))
    else:
        query = '''
            SELECT 
                u.id,
                u.email,
                u.name,
                u.created_at,
                u.subscription_status,
                u.questions_this_month,
                COUNT(c.id) as total_conversations
            FROM users u
            LEFT JOIN conversations c ON u.id = c.user_id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        '''
        df_users = pd.read_sql_query(query, conn)
    
    conn.close()
    
    if not df_users.empty:
        df_users.columns = [
            'ID', 'Email', 'Name', 'Joined', 
            'Status', 'Questions This Month', 'Total Conversations'
        ]
        df_users['Joined'] = pd.to_datetime(df_users['Joined']).dt.strftime('%Y-%m-%d %H:%M')
        df_users['Status'] = df_users['Status'].apply(lambda x: '💎 Paid' if x == 'paid' else '🆓 Free')
        
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        st.caption(f"**Showing {len(df_users)} users**")
    else:
        st.info("No users found" if search_query else "No users in database")


def show_active_users():
    """Show most active users"""
    st.subheader("🔥 Most Active Users")
    
    conn = sqlite3.connect('educapp_users.db')
    
    query = '''
        SELECT 
            u.name,
            u.email,
            u.subscription_status,
            COUNT(c.id) as conversation_count
        FROM users u
        LEFT JOIN conversations c ON u.id = c.user_id
        GROUP BY u.id
        HAVING conversation_count > 0
        ORDER BY conversation_count DESC
        LIMIT 20
    '''
    
    df_active = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df_active.empty:
        df_active.columns = ['Name', 'Email', 'Status', 'Conversations']
        df_active['Status'] = df_active['Status'].apply(lambda x: '💎 Paid' if x == 'paid' else '🆓 Free')
        
        # Add ranking
        df_active.insert(0, 'Rank', range(1, len(df_active) + 1))
        
        st.dataframe(df_active, use_container_width=True, hide_index=True)
        st.caption(f"**Top {len(df_active)} most active users**")
    else:
        st.info("No activity yet")


def show_recent_signups():
    """Show recent signups"""
    st.subheader("🆕 Recent Signups")
    
    # Date filter
    col1, col2 = st.columns([1, 3])
    with col1:
        days_back = st.selectbox("Show last:", [7, 14, 30, 60, 90], index=1)
    
    conn = sqlite3.connect('educapp_users.db')
    
    query = '''
        SELECT 
            name,
            email,
            created_at,
            subscription_status,
            questions_this_month
        FROM users
        WHERE created_at >= datetime('now', '-{} days')
        ORDER BY created_at DESC
    '''.format(days_back)
    
    df_recent = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df_recent.empty:
        df_recent.columns = ['Name', 'Email', 'Joined', 'Status', 'Questions Used']
        df_recent['Joined'] = pd.to_datetime(df_recent['Joined']).dt.strftime('%Y-%m-%d %H:%M')
        df_recent['Status'] = df_recent['Status'].apply(lambda x: '💎 Paid' if x == 'paid' else '🆓 Free')
        
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
        st.caption(f"**{len(df_recent)} new users in the last {days_back} days**")
    else:
        st.info(f"No new signups in the last {days_back} days")


def show_export_tools():
    """Export user data"""
    st.subheader("📤 Export User Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 Export User Emails")
        st.info("Download all user emails for newsletters, updates, and beta communications")
        
        if st.button("Download User Emails CSV", type="primary", use_container_width=True):
            conn = sqlite3.connect('educapp_users.db')
            query = '''
                SELECT email, name, created_at, subscription_status
                FROM users
                ORDER BY created_at DESC
            '''
            df_export = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df_export.empty:
                df_export.columns = ['Email', 'Name', 'Joined Date', 'Subscription']
                df_export['Joined Date'] = pd.to_datetime(df_export['Joined Date']).dt.strftime('%Y-%m-%d')
                
                csv = df_export.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download CSV File",
                    data=csv,
                    file_name=f"educapp_users_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success(f"✅ Ready! {len(df_export)} users")
            else:
                st.warning("No users to export")
    
    with col2:
        st.markdown("### 📊 Export Full User Data")
        st.info("Download complete user data including statistics and activity")
        
        if st.button("Download Full Data CSV", type="primary", use_container_width=True):
            conn = sqlite3.connect('educapp_users.db')
            query = '''
                SELECT 
                    u.id, u.email, u.name, u.created_at, 
                    u.subscription_status, u.subscription_start_date,
                    u.questions_this_month,
                    COUNT(c.id) as total_conversations
                FROM users u
                LEFT JOIN conversations c ON u.id = c.user_id
                GROUP BY u.id
                ORDER BY u.created_at DESC
            '''
            df_full = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df_full.empty:
                df_full.columns = [
                    'User ID', 'Email', 'Name', 'Joined Date',
                    'Subscription', 'Subscription Start',
                    'Questions This Month', 'Total Conversations'
                ]
                df_full['Joined Date'] = pd.to_datetime(df_full['Joined Date']).dt.strftime('%Y-%m-%d')
                df_full['Subscription Start'] = pd.to_datetime(df_full['Subscription Start'], errors='coerce').dt.strftime('%Y-%m-%d')
                
                csv = df_full.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download CSV File",
                    data=csv,
                    file_name=f"educapp_full_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                st.success(f"✅ Ready! Data for {len(df_full)} users")
            else:
                st.warning("No data to export")
    
    st.markdown("---")
    
    # Quick stats about export
    conn = sqlite3.connect('educapp_users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE subscription_status = "free"')
    free_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE subscription_status = "paid"')
    paid_count = cursor.fetchone()[0]
    
    conn.close()
    
    st.info(f"""
    **Export includes:**
    - {free_count} free users
    - {paid_count} paid users
    - Total: {free_count + paid_count} users
    """)


if __name__ == "__main__":
    check_password()
    show_user_dashboard()