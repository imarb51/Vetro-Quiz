"""Test Google Auth implementation."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_client_id():
    """Test if Google Client ID is properly loaded."""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    print(f"Google Client ID: {client_id}")
    
    if not client_id:
        print("❌ Google Client ID is not set!")
        return False
    
    if client_id and len(client_id) > 20:
        print("✅ Google Client ID is properly configured")
        return True
    else:
        print("❌ Google Client ID seems invalid")
        return False

def test_google_auth_endpoint():
    """Test Google auth with a dummy token."""
    from google_auth import GoogleAuth
    
    try:
        # This should fail gracefully
        GoogleAuth.verify_google_token("dummy_token")
    except Exception as e:
        print(f"Google Auth test with dummy token: {type(e).__name__}: {e}")
        return True  # Expected to fail

if __name__ == "__main__":
    print("🧪 Testing Google Auth Configuration...")
    print("-" * 50)
    
    # Test 1: Client ID
    test_google_client_id()
    
    print()
    
    # Test 2: Google Auth function
    test_google_auth_endpoint()
    
    print()
    print("🎯 Test completed!")