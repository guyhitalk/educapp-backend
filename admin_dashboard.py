# admin_dashboard.py
"""
EducApp Admin Dashboard
Monitor costs, users, and system health
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# SECURITY: Password protection (move to .env in production)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'educapp2024')

# Page config
st.set_page_config(
    page_title="EducApp Admin",
    page_icon="⚙️",
    layout="wide"
)

def check_password():
    """Password protection for admin dashboard"""
    
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.title("🔐 EducApp Admin Dashboard")
        st.write("Enter admin password to continue")
        
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password")
        
        st.stop()


def show_dashboard():
    """Main admin dashboard"""
    
    st.title("⚙️ EducApp Admin Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    # Import functions
    from core.database import (
        get_all_users_stats, 
        get_monthly_api_costs,
        get_top_users_by_cost,
        get_recent_api_calls
    )
    from core.usage_monitor import estimate_monthly_burn_rate
    
    # === OVERVIEW METRICS ===
    st.header("📊 Overview")
    
    try:
        user_stats = get_all_users_stats()
        burn_rate = estimate_monthly_burn_rate()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = burn_rate['free_users'] + burn_rate['paid_users']
            st.metric("Total Users", total_users)
        
        with col2:
            st.metric("Free Users", burn_rate['free_users'])
        
        with col3:
            st.metric("Paid Users", burn_rate['paid_users'])
        
        with col4:
            conversion_rate = (burn_rate['paid_users'] / total_users * 100) if total_users > 0 else 0
            st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        
        # === FINANCIAL METRICS ===
        st.header("💰 Financial Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Monthly Revenue", 
                f"${burn_rate['monthly_revenue']:.2f}",
                delta=f"R${burn_rate['monthly_revenue'] * 5:.2f}"
            )
        
        with col2:
            st.metric(
                "API Costs",
                f"${burn_rate['total_cost']:.2f}",
                delta=f"-${burn_rate['total_cost']:.2f}",
                delta_color="inverse"
            )
        
        with col3:
            profit_color = "normal" if burn_rate['profit_loss'] > 0 else "inverse"
            st.metric(
                "Net Profit/Loss",
                f"${burn_rate['profit_loss']:.2f}",
                delta=f"R${burn_rate['profit_loss'] * 5:.2f}",
                delta_color=profit_color
            )
        
        with col4:
            margin = (burn_rate['profit_loss'] / burn_rate['monthly_revenue'] * 100) if burn_rate['monthly_revenue'] > 0 else 0
            st.metric("Profit Margin", f"{margin:.1f}%")
        
        # === BREAK-EVEN ANALYSIS ===
        st.subheader("📈 Break-Even Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            users_to_break_even = max(0, burn_rate['total_cost'] / 19)
            status_message = "✅ Profitable!" if burn_rate['profit_loss'] > 0 else f"⚠️ Need {users_to_break_even - burn_rate['paid_users']:.0f} more users"
            
            st.info(f"""
**Current Status:**
- Need **{users_to_break_even:.0f} paying users** to break even
- Currently have **{burn_rate['paid_users']} paying users**
- {status_message}
            """)
        
        with col2:
            avg_cost_per_user = burn_rate['total_cost'] / total_users if total_users > 0 else 0
            avg_profit = 19 - (burn_rate['total_cost'] / burn_rate['paid_users']) if burn_rate['paid_users'] > 0 else 0
            
            st.info(f"""
**Per-User Economics:**
- Revenue per user: $19/month
- Avg cost per user: ${avg_cost_per_user:.2f}/month
- Avg profit per paid user: ${avg_profit:.2f}/month
            """)
        
        # === API USAGE STATS ===
        st.header("🔌 API Usage")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total API Calls", f"{burn_rate['total_calls']:,}")
        
        with col2:
            st.metric("Avg Cost per Call", f"${burn_rate['avg_cost_per_call']:.4f}")
        
        with col3:
            calls_per_user = burn_rate['total_calls'] / total_users if total_users > 0 else 0
            st.metric("Avg Calls per User", f"{calls_per_user:.1f}")
        
        # === TOP USERS BY COST ===
        st.header("🔥 Top Users by API Cost")
        
        top_users = get_top_users_by_cost(limit=10)
        
        if top_users:
            df_top_users = pd.DataFrame(
                top_users,
                columns=['Email', 'Name', 'Status', 'Total Calls', 'Total Cost ($)']
            )
            df_top_users['Total Cost (R$)'] = df_top_users['Total Cost ($)'] * 5
            df_top_users['Total Cost ($)'] = df_top_users['Total Cost ($)'].round(2)
            df_top_users['Total Cost (R$)'] = df_top_users['Total Cost (R$)'].round(2)
            
            st.dataframe(df_top_users, use_container_width=True)
        else:
            st.info("No usage data yet")
        
        # === RECENT API CALLS ===
        st.header("📝 Recent API Calls")
        
        recent_calls = get_recent_api_calls(limit=20)
        
        if recent_calls:
            df_recent = pd.DataFrame(
                recent_calls,
                columns=['User Email', 'Input Tokens', 'Output Tokens', 'Cost ($)', 'Timestamp', 'Model']
            )
            df_recent['Cost (R$)'] = df_recent['Cost ($)'] * 5
            df_recent['Cost ($)'] = df_recent['Cost ($)'].round(4)
            df_recent['Cost (R$)'] = df_recent['Cost (R$)'].round(2)
            
            st.dataframe(df_recent, use_container_width=True)
        else:
            st.info("No API calls yet")
        
        # === MANUAL CONTROLS ===
        st.header("🛠️ Manual Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Upgrade User to Paid")
            user_email = st.text_input("User Email")
            if st.button("Upgrade to Paid"):
                if user_email:
                    from core.database import upgrade_to_paid
                    upgrade_to_paid(user_email)
                    st.success(f"✅ Upgraded {user_email} to paid!")
                    st.rerun()
                else:
                    st.error("Please enter an email")
        
        with col2:
            st.subheader("Database Stats")
            
            try:
                conn = sqlite3.connect('educapp.db')
                
                total_conversations = pd.read_sql("SELECT COUNT(*) as count FROM conversations", conn)
                total_api_calls = pd.read_sql("SELECT COUNT(*) as count FROM api_usage", conn)
                
                db_size = os.path.getsize('educapp.db') / 1024
                
                st.info(f"""
**Database Information:**
- Total Conversations: {total_conversations['count'][0]:,}
- Total API Calls: {total_api_calls['count'][0]:,}
- Database Size: {db_size:.1f} KB
                """)
                
                conn.close()
            except Exception as e:
                st.error(f"Error reading database: {e}")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.exception(e)


if __name__ == "__main__":
    check_password()
    show_dashboard()