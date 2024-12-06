from true_storage.store import (
    FileSystemStorage,
    SQLiteStorage,
    RedisStorage,
    ColdStorage,
    HotStorage,
    MixedStorage,
    SessionStore,
    SessionStoreConfig
)

def demo_filesystem_storage():
    print("\n=== FileSystem Storage Demo ===")
    fs_storage = FileSystemStorage()
    
    # Store some data
    fs_storage.store("user1", {"name": "John Doe", "age": 30})
    
    # Retrieve data
    user = fs_storage.retrieve("user1")
    print(f"Retrieved user: {user}")
    
    # Delete data
    fs_storage.delete("user1")
    print("User deleted")

def demo_sqlite_storage():
    print("\n=== SQLite Storage Demo ===")
    sql_storage = SQLiteStorage(":memory:")  # Using in-memory database for demo
    
    try:
        # Store data
        sql_storage.store("config", {"theme": "dark", "language": "en"})
        
        # Retrieve data
        config = sql_storage.retrieve("config")
        print(f"Retrieved config: {config}")
        
        # Clear all data
        sql_storage.clear()
        print("Storage cleared")
    except Exception as e:
        print(f"SQLite demo failed: {e}")

def demo_hot_storage():
    print("\n=== Hot Storage Demo ===")
    hot_storage = HotStorage(max_size=2, expiration_time=5)
    
    # Store items
    hot_storage.store("key1", "value1")
    hot_storage.store("key2", "value2")
    
    # Demonstrate max size limit
    hot_storage.store("key3", "value3")  # This will evict the oldest item
    
    try:
        value = hot_storage.retrieve("key1")
        print("Key1 value:", value)
    except KeyError:
        print("Key1 was evicted due to max size limit")
    
    print("Key2 value:", hot_storage.retrieve("key2"))
    print("Key3 value:", hot_storage.retrieve("key3"))

def demo_cold_storage():
    print("\n=== Cold Storage Demo ===")
    cold_storage = ColdStorage(storage_directory="demo_cold_storage")
    
    # Store data with compression
    data = {"large_data": "x" * 1000}  # Some large data
    cold_storage.store("compressed_data", data)
    
    # Retrieve data
    retrieved_data = cold_storage.retrieve("compressed_data")
    print(f"Retrieved data length: {len(retrieved_data['large_data'])}")
    
    # Clean up
    cold_storage.clear()

def demo_mixed_storage():
    print("\n=== Mixed Storage Demo ===")
    mixed_storage = MixedStorage(max_size=100, expiration_time=300)
    
    # Store session data
    session_data = {"user_id": 123, "permissions": ["read", "write"]}
    mixed_storage.store_session("session1", session_data)
    
    # Retrieve session
    retrieved_session = mixed_storage.retrieve_session("session1")
    print(f"Retrieved session: {retrieved_session}")

def demo_session_store():
    print("\n=== Session Store Demo ===")
    config = SessionStoreConfig(max_size=1000, expiration_time=3600)
    session_store = SessionStore(config=config)
    
    # Set session data
    session_store.set("user_session", {
        "user_id": 456,
        "login_time": "2023-01-01 12:00:00"
    })
    
    # Get session data
    session = session_store.get("user_session")
    print(f"Active session: {session}")
    
    # Clean up
    session_store.stop_cleanup()

def main():
    print("True Storage Demo\n")
    
    # Run demos
    demo_filesystem_storage()
    demo_sqlite_storage()
    demo_hot_storage()
    demo_cold_storage()
    demo_mixed_storage()
    demo_session_store()

if __name__ == "__main__":
    main()
