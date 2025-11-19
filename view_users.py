"""
View all registered users in EducApp
"""
import sqlite3
from datetime import datetime

def view_all_users():
    """Display all users in the database"""
    conn = sqlite3.connect('educapp_users.db')
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute('''
        SELECT id, email, name, created_at, subscription_status, questions_this_month
        FROM users
        ORDER BY created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("📭 No users found in database")
        return
    
    print(f"\n👥 TOTAL USERS: {len(users)}")
    print("=" * 100)
    
    for user in users:
        user_id, email, name, created_at, subscription, questions = user
        print(f"\n🆔 ID: {user_id}")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {name}")
        print(f"📅 Joined: {created_at}")
        print(f"💳 Status: {subscription}")
        print(f"❓ Questions This Month: {questions}")
        print("-" * 100)

def export_emails_to_csv():
    """Export all user emails to a CSV file"""
    import csv
    
    conn = sqlite3.connect('educapp_users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT email, name, created_at, subscription_status
        FROM users
        ORDER BY created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    # Create CSV file
    filename = f'educapp_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Email', 'Name', 'Joined Date', 'Subscription Status'])
        
        for user in users:
            writer.writerow(user)
    
    print(f"\n✅ Exported {len(users)} users to: {filename}")
    return filename

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("📊 EDUCAPP USER DATABASE")
    print("=" * 100)
    
    view_all_users()
    
    print("\n" + "=" * 100)
    response = input("\n📤 Export emails to CSV? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        export_emails_to_csv()
        print("\n✅ Done! You can open the CSV file in Excel or Google Sheets")
    
    print("\n" + "=" * 100)