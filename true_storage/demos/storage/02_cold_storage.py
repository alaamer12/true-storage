"""
Cold Storage Demo

This demo shows operations with the True Storage cold storage system,
which provides compressed, long-term storage capabilities with metadata tracking.
"""

import logging
import json
import tempfile
import time
from datetime import datetime
from true_storage.storage.cold import ColdStorage

def format_size(size_bytes):
    """Format size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create a temporary directory for cold storage
    with tempfile.TemporaryDirectory() as temp_dir:
        print("Initializing cold storage...")
        storage = ColdStorage(
            storage_directory=temp_dir,
            compression_level=6  # Medium compression
        )

        print("\nStoring different types of data...")

        # 1. Store large text data
        print("\nStoring large text data:")
        large_text = "This is a sample text that will be compressed." * 1000
        storage.store("text_data", large_text)
        text_meta = storage.get_item_metadata("text_data")
        print(f"Stored text data (compressed size: {format_size(text_meta['size'])})")

        # 2. Store structured data
        print("\nStoring structured data:")
        structured_data = {
            "project": "True Storage Demo",
            "created_at": datetime.now().isoformat(),
            "settings": {
                "compression": True,
                "backup_enabled": True,
                "retention_days": 30
            },
            "data_points": [
                {"id": i, "value": f"point_{i}"} 
                for i in range(100)
            ]
        }
        storage.store("config_data", structured_data)
        config_meta = storage.get_item_metadata("config_data")
        print(f"Stored configuration data (compressed size: {format_size(config_meta['size'])})")

        # 3. Store binary data
        print("\nStoring binary data:")
        binary_data = bytes([i % 256 for i in range(10000)])
        storage.store("binary_data", binary_data)
        binary_meta = storage.get_item_metadata("binary_data")
        print(f"Stored binary data (compressed size: {format_size(binary_meta['size'])})")

        # Display storage statistics
        print("\nCurrent storage statistics:")
        stats = storage.get_stats()
        print(f"Total items: {stats['total_items']}")
        print(f"Total size: {format_size(stats['total_size'])}")
        print(f"Average item size: {format_size(stats['avg_item_size'])}")
        print(f"Average response time: {stats['avg_response_time']:.2f}ms")

        # Demonstrate data retrieval
        print("\nRetrieving and verifying data...")
        
        # Verify text data
        retrieved_text = storage.retrieve("text_data")
        print(f"Retrieved text data matches: {retrieved_text == large_text}")
        
        # Verify structured data
        retrieved_config = storage.retrieve("config_data")
        print(f"Retrieved config data matches: {retrieved_config == structured_data}")
        
        # Verify binary data
        retrieved_binary = storage.retrieve("binary_data")
        print(f"Retrieved binary data matches: {retrieved_binary == binary_data}")

        # Show item metadata
        print("\nItem metadata:")
        for key in storage.get_keys():
            meta = storage.get_item_metadata(key)
            created = datetime.fromtimestamp(meta['created_at'])
            last_accessed = datetime.fromtimestamp(meta['last_accessed'])
            print(f"\n{key}:")
            print(f"  Size: {format_size(meta['size'])}")
            print(f"  Created: {created}")
            print(f"  Last accessed: {last_accessed}")

        # Demonstrate deletion
        print("\nDemonstrating deletion...")
        storage.delete("binary_data")
        print("Deleted binary data")
        print(f"Remaining items: {storage.get_keys()}")

        # Final statistics
        print("\nFinal storage statistics:")
        stats = storage.get_stats()
        print(f"Total items: {stats['total_items']}")
        print(f"Total size: {format_size(stats['total_size'])}")
        print(f"Hit ratio: {stats['hit_ratio']:.2%}")
        print(f"Total operations: {stats['total_operations']}")

if __name__ == "__main__":
    main()
