import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

print("Testing Supabase Connection...")
print("-" * 50)

# Get credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"SUPABASE_URL: {url[:30]}..." if url else "SUPABASE_URL: NOT FOUND")
print(f"SUPABASE_KEY: {key[:30]}..." if key else "SUPABASE_KEY: NOT FOUND")
print("-" * 50)

if not url or not key:
    print("❌ ERROR: Missing credentials in .env file")
    exit(1)

try:
    # Try to connect
    client = create_client(url, key)
    print("✅ Connection object created successfully!")
    
    # Try a simple query
    response = client.table('users').select("*").limit(1).execute()
    print("✅ Database query successful!")
    print(f"✅ Connection to Supabase working perfectly!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nPossible issues:")
    print("1. Check your SUPABASE_URL and SUPABASE_KEY in .env")
    print("2. Check your internet connection")
    print("3. Verify your Supabase project is active")
    print("4. Tables might not exist yet (this is okay - we can create them)")