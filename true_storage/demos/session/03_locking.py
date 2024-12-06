"""
Session Locking Demo

This demo shows how to use session locking for thread-safe operations.
"""

import threading
import time
from true_storage.session import SessionStore, SessionStoreConfig, StorageError

def worker(name: str, store: SessionStore, key: str):
    """Worker function that tries to access and modify a locked session."""
    try:
        print(f"\n👤 Worker {name}: Attempting to access key '{key}'")
        value = store.get(key)
        print(f"👤 Worker {name}: Read value: {value}")
        
        # Try to modify the value
        new_value = f"Modified by {name}"
        store.set(key, new_value)
        print(f"👤 Worker {name}: Successfully modified value to: {new_value}")
        
    except StorageError as e:
        print(f"❌ Worker {name}: Access denied - {e}")

def main():
    # Initialize session store with shorter lock timeout
    print("🚀 Initializing session store...")
    config = SessionStoreConfig(
        max_size=100,
        max_lock_time=5  # 5 seconds maximum lock time
    )
    store = SessionStore(config)
    
    # Set initial data
    key = 'shared_data'
    store.set(key, 'Initial value')
    
    # Demonstrate basic locking
    print("\n🔒 Basic locking demonstration:")
    print(f"Initial value: {store.get(key)}")
    
    # Lock the session
    print("\nLocking session...")
    store.lock(key)
    
    # Try to access locked session
    try:
        store.set(key, 'New value')
        print("✅ Set new value (shouldn't happen when locked)")
    except StorageError as e:
        print(f"❌ Failed to set value: {e}")
    
    # Check lock status
    status = store.get_status(key)
    print(f"\n📊 Session status: {status}")
    
    # Unlock the session
    print("\n🔓 Unlocking session...")
    store.unlock(key)
    
    # Demonstrate concurrent access
    print("\n🔄 Demonstrating concurrent access...")
    
    # Lock the session again
    store.lock(key)
    
    # Create worker threads
    threads = []
    for i in range(3):
        thread = threading.Thread(
            target=worker,
            args=(f"Worker-{i}", store, key)
        )
        threads.append(thread)
        thread.start()
    
    # Wait a bit before unlocking
    print("\n⏳ Waiting with lock held...")
    time.sleep(2)
    
    # Unlock for workers
    print("\n🔓 Unlocking for workers...")
    store.unlock(key)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Show final value
    print(f"\n📝 Final value: {store.get(key)}")
    
    # Demonstrate lock timeout
    print("\n⏲️ Demonstrating lock timeout...")
    store.lock(key, duration=3)  # Lock for 3 seconds
    print("Session locked for 3 seconds")
    
    print("Waiting for lock to expire...")
    time.sleep(4)
    
    # Try to access after timeout
    try:
        store.set(key, 'After timeout')
        print("✅ Successfully set value after lock timeout")
    except StorageError as e:
        print(f"❌ Failed to set value: {e}")
    
    # Stop the session store
    print("\n🛑 Stopping session store...")
    store.stop()

if __name__ == '__main__':
    main()
