"""
Basic Session Management Demo

This demo shows the fundamental operations of the True Storage session management system.
"""

from true_storage.session import SessionStore, SessionStoreConfig

def main():
    # Initialize session store with default configuration
    print("🚀 Initializing session store...")
    store = SessionStore()
    
    # Basic key-value operations
    print("\n📝 Basic key-value operations:")
    store['user_id'] = 'user123'  # Dict-style setting
    store.set('username', 'John Doe')  # Method-style setting
    
    print(f"User ID: {store.get('user_id')}")
    print(f"Username: {store['username']}")  # Dict-style getting
    
    # Default values
    print("\n🔄 Using default values:")
    print(f"Age (with default): {store.get('age', default=25)}")
    print(f"Email (with default): {store.get('email', default='no-email')}")
    
    # Check key existence
    print("\n🔍 Checking key existence:")
    print(f"'user_id' exists: {'user_id' in store}")
    print(f"'age' exists: {'age' in store}")
    
    # Store different types of data
    print("\n📦 Storing different data types:")
    store.set('numbers', [1, 2, 3, 4, 5])
    store.set('config', {'theme': 'dark', 'language': 'en'})
    store.set('is_active', True)
    
    print(f"Numbers: {store.get('numbers')}")
    print(f"Config: {store.get('config')}")
    print(f"Is Active: {store.get('is_active')}")
    
    # Delete operations
    print("\n❌ Delete operations:")
    store.delete('username')
    print(f"After deletion, username exists: {'username' in store}")
    
    # Clear all sessions
    print("\n🧹 Clearing all sessions...")
    store.clear()
    print(f"Store size after clear: {len(store)}")

if __name__ == '__main__':
    main()
