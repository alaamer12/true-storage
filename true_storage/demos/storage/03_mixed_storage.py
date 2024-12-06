"""
Mixed Storage Demo

This demo shows operations with the True Storage mixed storage system,
which combines hot and cold storage for optimal performance and storage efficiency.
"""

import logging
import time
import tempfile
from datetime import datetime
from true_storage.storage.mixed import MixedStorage

def format_size(size_bytes):
    """Format size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def measure_time(func):
    """Decorator to measure execution time."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"Operation took: {(end - start)*1000:.2f}ms")
        return result
    return wrapper

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Create temporary directory for cold storage
    with tempfile.TemporaryDirectory() as temp_dir:
        print("Initializing mixed storage...")
        storage = MixedStorage(
            storage_directory=temp_dir,
            max_size=5,  # Small hot storage size for demonstration
            expiration_time=10,  # Short expiration for demonstration
            compression_level=6
        )

        print("\nDemonstrating tiered storage...")

        # 1. Store frequently accessed data
        print("\nStoring frequently accessed data:")
        frequent_data = {
            "type": "frequent",
            "timestamp": datetime.now().isoformat(),
            "data": "This is frequently accessed data" * 100
        }
        storage.store("frequent_data", frequent_data)

        # 2. Store rarely accessed data
        print("\nStoring rarely accessed data:")
        rare_data = {
            "type": "rare",
            "timestamp": datetime.now().isoformat(),
            "data": "This is rarely accessed data" * 100
        }
        storage.store("rare_data", rare_data)

        # Display initial statistics
        print("\nInitial storage statistics:")
        stats = storage.get_stats()
        print("\nHot Storage:")
        hot_stats = stats["hot_storage"]
        print(f"Size: {hot_stats['size']} items")
        print(f"Max size: {hot_stats['max_size']} items")
        print(f"Hit ratio: {hot_stats['hit_ratio']:.2%}")
        print(f"Average response time: {hot_stats['avg_response_time']:.2f}ms")

        print("\nCold Storage:")
        cold_stats = stats["cold_storage"]
        print(f"Total items: {cold_stats['total_items']}")
        print(f"Total size: {format_size(cold_stats['total_size'])}")
        print(f"Average item size: {format_size(cold_stats['avg_item_size'])}")

        # Demonstrate access patterns
        print("\nSimulating access patterns...")

        @measure_time
        def access_frequent_data():
            """Access frequent data multiple times."""
            for _ in range(5):
                value = storage.retrieve("frequent_data")
                print(f"Retrieved frequent data (type: {value['type']})")
                time.sleep(0.1)  # Simulate processing

        @measure_time
        def access_rare_data():
            """Access rare data once."""
            value = storage.retrieve("rare_data")
            print(f"Retrieved rare data (type: {value['type']})")
            time.sleep(0.1)  # Simulate processing

        print("\nAccessing frequent data multiple times:")
        access_frequent_data()

        print("\nAccessing rare data once:")
        access_rare_data()

        # Store more data to demonstrate hot storage eviction
        print("\nStoring additional data to demonstrate hot storage eviction...")
        for i in range(5):
            data = {
                "type": f"additional_{i}",
                "timestamp": datetime.now().isoformat(),
                "data": f"Additional data {i}" * 50
            }
            storage.store(f"additional_{i}", data)
            print(f"Stored additional_{i}")

        # Optimize hot storage
        print("\nOptimizing hot storage...")
        storage.optimize_hot_storage()

        # Show keys in both storages
        print("\nKeys in storage after optimization:")
        keys = storage.get_keys()
        print(f"Total keys: {len(keys)}")
        print(f"Keys: {keys}")

        # Warm up hot storage with specific keys
        print("\nWarming up hot storage with frequent data...")
        storage.warm_up_hot_storage(["frequent_data"])

        # Final statistics
        print("\nFinal storage statistics:")
        stats = storage.get_stats()
        
        print("\nHot Storage:")
        hot_stats = stats["hot_storage"]
        print(f"Size: {hot_stats['size']} items")
        print(f"Max size: {hot_stats['max_size']} items")
        print(f"Hit ratio: {hot_stats['hit_ratio']:.2%}")
        print(f"Average response time: {hot_stats['avg_response_time']:.2f}ms")

        print("\nCold Storage:")
        cold_stats = stats["cold_storage"]
        print(f"Total items: {cold_stats['total_items']}")
        print(f"Total size: {format_size(cold_stats['total_size'])}")
        print(f"Average item size: {format_size(cold_stats['avg_item_size'])}")

        print("\nCombined Statistics:")
        combined_stats = stats["combined"]
        print(f"Total operations: {combined_stats['total_operations']}")
        print(f"Hit ratio: {combined_stats['hit_ratio']:.2%}")
        print(f"Average response time: {combined_stats['avg_response_time']:.2f}ms")

if __name__ == "__main__":
    main()
