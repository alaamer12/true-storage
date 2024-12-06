"""
Session Expiration and Cleanup Demo

This demo demonstrates session expiration and cleanup features of True Storage.
"""

import time
from true_storage.session import SessionStore, SessionStoreConfig

def main():
    # Initialize session store with custom expiration settings
    print("🚀 Initializing session store with custom expiration...")
    config = SessionStoreConfig(
        max_size=100,
        expiration_time=5,  # 5 seconds expiration
        cleanup_interval=2   # Clean up every 2 seconds
    )
    store = SessionStore(config)
    
    # Set some session data
    print("\n📝 Setting session data...")
    store.set('quick_expire', 'This will expire in 5 seconds')
    store.set('user_data', {'name': 'John', 'age': 30})
    
    print("Initial data:")
    print(f"quick_expire: {store.get('quick_expire')}")
    print(f"user_data: {store.get('user_data')}")
    
    # Wait for expiration
    print("\n⏳ Waiting for session expiration (6 seconds)...")
    time.sleep(6)
    
    print("\nAfter waiting:")
    print(f"quick_expire exists: {'quick_expire' in store}")
    print(f"quick_expire value: {store.get('quick_expire', 'EXPIRED!')}")
    print(f"user_data exists: {'user_data' in store}")
    
    # Set data with different expiration times
    print("\n🕒 Setting data with different expiration times...")
    store.set('short_lived', 'Expires quickly')
    store.set('long_lived', 'Stays longer')
    
    print("\nInitial state:")
    print(f"short_lived: {store.get('short_lived')}")
    print(f"long_lived: {store.get('long_lived')}")
    
    print("\n⏳ Waiting for 3 seconds...")
    time.sleep(3)
    
    print("\nAfter 3 seconds:")
    print(f"short_lived: {store.get('short_lived', 'EXPIRED!')}")
    print(f"long_lived: {store.get('long_lived', 'EXPIRED!')}")
    
    # Check session metadata
    print("\n📊 Checking session metadata...")
    if metadata := store.get_metadata('long_lived'):
        print(f"Created at: {metadata.created_at}")
        print(f"Last accessed: {metadata.last_accessed}")
        print(f"Access count: {metadata.access_count}")
        print(f"Status: {metadata.status}")
    
    # Demonstrate cleanup
    print("\n🧹 Demonstrating cleanup...")
    print(f"Store size before cleanup: {len(store)}")
    time.sleep(3)  # Wait for cleanup cycle
    print(f"Store size after cleanup: {len(store)}")
    
    # Stop the session store properly
    print("\n🛑 Stopping session store...")
    store.stop()

if __name__ == '__main__':
    main()
