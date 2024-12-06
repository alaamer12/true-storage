"""Basic SQLite Storage Demo

This demo shows basic operations with the SQLite storage backend.
"""

import logging
from true_storage.database import SQLiteStorage

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("🚀 Initializing SQLite Store...")
    # Create an in-memory database for demonstration
    store = SQLiteStorage(":memory:")

    print("\n📝 Storing and retrieving data...")
    
    # Store some user data
    user1 = {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com"
    }
    user2 = {
        "id": 2,
        "name": "Bob",
        "email": "bob@example.com"
    }
    
    # Store users
    store.store("user:1", user1)
    store.store("user:2", user2)
    print("✅ Stored user data")

    # Retrieve users
    retrieved_user1 = store.retrieve("user:1")
    print(f"\nRetrieved User 1:")
    print(f"Name: {retrieved_user1['name']}")
    print(f"Email: {retrieved_user1['email']}")

    retrieved_user2 = store.retrieve("user:2")
    print(f"\nRetrieved User 2:")
    print(f"Name: {retrieved_user2['name']}")
    print(f"Email: {retrieved_user2['email']}")

    # Delete a user
    print("\n🗑️ Deleting User 1...")
    store.delete("user:1")
    
    try:
        store.retrieve("user:1")
    except KeyError:
        print("✅ User 1 successfully deleted")

    # Clear all data
    print("\n🧹 Clearing all data...")
    store.clear()
    
    try:
        store.retrieve("user:2")
    except KeyError:
        print("✅ All data successfully cleared")

if __name__ == "__main__":
    main()
