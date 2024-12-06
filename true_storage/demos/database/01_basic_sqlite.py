"""
Basic SQLite Demo

This demo shows basic operations with the SQLite database backend.
"""

import logging
from true_storage.database.sqlite import SQLiteStore

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print("🚀 Initializing SQLite Store...")
    # Create an in-memory database for demonstration
    store = SQLiteStore(":memory:")

    # Create a table
    print("\n📝 Creating a sample table...")
    store.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """)

    # Insert data
    print("\n➕ Inserting sample data...")
    users = [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
        ("Charlie", "charlie@example.com")
    ]
    
    for name, email in users:
        store.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )

    # Query data
    print("\n🔍 Querying all users:")
    results = store.execute("SELECT * FROM users")
    for row in results:
        print(f"User {row[0]}: {row[1]} ({row[2]})")

    # Update data
    print("\n✏️ Updating user data...")
    store.execute(
        "UPDATE users SET email = ? WHERE name = ?",
        ("alice.new@example.com", "Alice")
    )

    # Query specific user
    print("\n🔍 Querying specific user:")
    result = store.execute(
        "SELECT * FROM users WHERE name = ?",
        ("Alice",)
    ).fetchone()
    print(f"Updated user: {result[1]} ({result[2]})")

    # Delete data
    print("\n❌ Deleting user...")
    store.execute("DELETE FROM users WHERE name = ?", ("Bob",))

    # Final count
    print("\n📊 Final user count:")
    count = store.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"Remaining users: {count}")

    # Demonstrate transaction
    print("\n🔄 Demonstrating transaction...")
    try:
        with store.transaction():
            store.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                ("Dave", "dave@example.com")
            )
            # Simulate an error
            if True:  # For demonstration
                raise Exception("Simulated error")
            store.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                ("Eve", "eve@example.com")
            )
    except Exception as e:
        print(f"Transaction rolled back: {e}")

    # Show final state
    print("\n📋 Final database state:")
    results = store.execute("SELECT * FROM users")
    for row in results:
        print(f"User {row[0]}: {row[1]} ({row[2]})")

    print("\n✨ Demo completed!")

if __name__ == "__main__":
    main()
