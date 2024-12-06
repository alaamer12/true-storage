"""
Filesystem Store Demo

This demo shows operations with the filesystem-based storage backend.
"""

import os
import json
import tempfile
import logging
from pathlib import Path
from true_storage.database.filesystem import FileSystemStore

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create a temporary directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🚀 Initializing FileSystem Store in {temp_dir}...")
        store = FileSystemStore(temp_dir)

        # Store some data
        print("\n💾 Storing data...")
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
        print("\n📁 Creating directory structure...")
        store.store("config/app.json", json.dumps(data["config"]))
        store.store("data/users.json", json.dumps(data["users"]))

        # List directory contents
        print("\n📋 Directory structure:")
        def print_tree(path, prefix=""):
            path_obj = Path(temp_dir) / path
            if path_obj.is_file():
                size = path_obj.stat().st_size
                print(f"{prefix}📄 {path_obj.name} ({size} bytes)")
            else:
                print(f"{prefix}📁 {path_obj.name}/")
                for child in path_obj.iterdir():
                    print_tree(child.relative_to(Path(temp_dir)), prefix + "  ")

        print_tree("")

        # Read data back
        print("\n📖 Reading configuration...")
        config = json.loads(store.retrieve("config/app.json"))
        print("App Configuration:")
        print(f"  Name: {config['app_name']}")
        print(f"  Version: {config['version']}")
        print(f"  Debug Mode: {config['settings']['debug']}")

        print("\n👥 Reading users...")
        users = json.loads(store.retrieve("data/users.json"))
        for user in users:
            print(f"  User {user['id']}: {user['name']} ({user['role']})")

        # Update data
        print("\n✏️ Updating configuration...")
        config["settings"]["debug"] = False
        store.store("config/app.json", json.dumps(config))

        # Verify update
        print("\n🔍 Verifying update...")
        updated_config = json.loads(store.retrieve("config/app.json"))
        print(f"Debug Mode is now: {updated_config['settings']['debug']}")

        # Delete data
        print("\n❌ Deleting user data...")
        store.delete("data/users.json")

        # Check existence
        print("\n✨ Checking file existence:")
        files = ["config/app.json", "data/users.json"]
        for file in files:
            exists = store.exists(file)
            print(f"  {file}: {'✅ Exists' if exists else '❌ Not found'}")

        print("\n🧹 Cleanup will happen automatically when exiting the context")

    print("\n✨ Demo completed!")

if __name__ == "__main__":
    main()
