"""
Filesystem Store Demo

This demo shows operations with the filesystem-based storage backend.
"""

import json
import tempfile
import logging
from pathlib import Path
from true_storage.database import FileSystemStorage

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create a temporary directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nInitializing FileSystem Store in {temp_dir}...")
        store = FileSystemStorage(temp_dir)

        # Store some data
        print("\nStoring data...")
        data = {
            "config": {
                "app_name": "Demo App",
                "version": "1.0.0",
                "settings": {
                    "debug": True,
                    "max_connections": 100
                }
            },
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"}
            ]
        }

        # Store data in different paths
        print("\nCreating directory structure...")
        store.store("config/app.json", data["config"])  # Store Python dict directly
        store.store("data/users.json", data["users"])   # Store Python list directly

        # Read data back
        print("\nReading configuration...")
        config = store.retrieve("config/app.json")  # Retrieved as Python dict
        print("App Configuration:")
        print(f"  Name: {config['app_name']}")
        print(f"  Version: {config['version']}")
        print(f"  Debug Mode: {config['settings']['debug']}")

        print("\nReading users...")
        users = store.retrieve("data/users.json")  # Retrieved as Python list
        for user in users:
            print(f"  User {user['id']}: {user['name']} ({user['role']})")

        # Update data
        print("\nUpdating configuration...")
        config["settings"]["debug"] = False
        store.store("config/app.json", config)

        # Verify update
        print("\nVerifying update...")
        updated_config = store.retrieve("config/app.json")
        print(f"Debug Mode is now: {updated_config['settings']['debug']}")

        # Delete data
        print("\nDeleting user data...")
        store.delete("data/users.json")

        # Check existence
        print("\nChecking file existence:")
        files = ["config/app.json", "data/users.json"]
        for file in files:
            exists = store.exists(file)
            print(f"  {file}: {'Exists' if exists else 'Not found'}")

        print("\nCleanup will happen automatically when exiting the context")

    print("\nDemo completed!")

if __name__ == "__main__":
    main()
