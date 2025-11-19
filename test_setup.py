# Test if everything is installed correctly

print("Testing imports...")

try:
    import openai
    print("✓ OpenAI installed")
except ImportError:
    print("✗ OpenAI NOT installed")

try:
    import langchain
    print("✓ LangChain installed")
except ImportError:
    print("✗ LangChain NOT installed")

try:
    import streamlit
    print("✓ Streamlit installed")
except ImportError:
    print("✗ Streamlit NOT installed")

try:
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and api_key != "your_key_will_go_here":
        print(f"✓ API key loaded (starts with: {api_key[:8]}...)")
    else:
        print("⚠ API key placeholder detected - you need to add your real OpenAI key")
except Exception as e:
    print(f"✗ Error loading API key: {e}")

print("\nSetup test complete!")