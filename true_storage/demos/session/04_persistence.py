"""
Session Persistence and Recovery Demo

This demo shows how to use session persistence features for data durability.
"""

import os
import time
from pathlib import Path
from true_storage.session import SessionStore, SessionStoreConfig

def main():
    # Setup persistence directory
    persistence_dir = Path("session_data")
    persistence_dir.mkdir(exist_ok=True)
    persistence_path = str(persistence_dir / "sessions.json")
    
    # Initialize session store with persistence
    print("🚀 Initializing session store with persistence...")
    config = SessionStoreConfig(
        max_size=100,
        persistence_path=persistence_path,
        backup_interval=5,  # Backup every 5 seconds
        enable_logging=True
    )
    store = SessionStore(config)
    
    # Check if we have any restored sessions
    print("\n📥 Checking for restored sessions...")
    print(f"Current store size: {len(store)}")
    
    # Set some session data
    print("\n📝 Setting new session data...")
    store.set('user_prefs', {
        'theme': 'dark',
        'language': 'en',
        'notifications': True
    })
    store.set('cart_items', [
        {'id': 1, 'name': 'Widget', 'quantity': 2},
        {'id': 2, 'name': 'Gadget', 'quantity': 1}
    ])
    
    # Wait for automatic backup
    print("\n⏳ Waiting for automatic backup (6 seconds)...")
    time.sleep(6)
    
    # Verify data was persisted
    print("\n🔍 Verifying persistence file...")
    if os.path.exists(persistence_path):
        print(f"✅ Persistence file exists at: {persistence_path}")
        print(f"File size: {os.path.getsize(persistence_path)} bytes")
    
    # Simulate application restart
    print("\n🔄 Simulating application restart...")
    store.stop()
    
    print("\n⏳ Waiting a moment...")
    time.sleep(2)
    
    # Create new store instance
    print("\n🚀 Creating new store instance...")
    new_store = SessionStore(config)
    
    # Verify data was restored
    print("\n🔍 Verifying restored data...")
    print("\nRestored user preferences:")
    print(new_store.get('user_prefs'))
    print("\nRestored cart items:")
    print(new_store.get('cart_items'))
    
    # Demonstrate atomic updates
    print("\n⚡ Demonstrating atomic updates...")
    for i in range(5):
        new_store.set(f'counter_{i}', i)
        print(f"Set counter_{i} = {i}")
        time.sleep(1)  # Allow time for backup
    
    # Final verification
    print("\n📊 Final store statistics:")
    print(f"Total sessions: {len(new_store)}")
    print(f"Persistence file size: {os.path.getsize(persistence_path)} bytes")
    
    # Clean up
    print("\n🧹 Cleaning up...")
    new_store.stop()
    
    # Optionally remove persistence file
    if input("\nRemove persistence file? (y/n): ").lower() == 'y':
        os.remove(persistence_path)
        persistence_dir.rmdir()
        print("✅ Persistence file and directory removed")
    else:
        print(f"ℹ️ Persistence file kept at: {persistence_path}")

if __name__ == '__main__':
    main()
