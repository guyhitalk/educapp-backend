from core.conversation_manager import ConversationManager

# Initialize manager
conv_mgr = ConversationManager()

# Test save (use user_id = 1 for testing)
print("Testing conversation save...")
success = conv_mgr.save_conversation(
    user_id=1,
    question="What is 2+2?",
    answer="2+2 equals 4. This is a fundamental arithmetic operation...",
    subject="Mathematics"
)

if success:
    print("✅ Conversation saved successfully!")
else:
    print("❌ Failed to save conversation")

# Test retrieve
print("\nTesting conversation retrieval...")
conversations = conv_mgr.get_user_conversations(user_id=1)
print(f"✅ Found {len(conversations)} conversations")

if conversations:
    print("\nMost recent conversation:")
    print(f"Q: {conversations[0]['question']}")
    print(f"A: {conversations[0]['answer'][:100]}...")
    print(f"Subject: {conversations[0]['subject']}")
    print(f"Time: {conversations[0]['timestamp']}")

# Test count
count = conv_mgr.get_conversation_count(user_id=1)
print(f"\n✅ Total conversations for user: {count}")