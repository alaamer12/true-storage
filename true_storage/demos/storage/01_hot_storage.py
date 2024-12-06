"""
Hot Storage Demo

This demo shows operations with the True Storage hot storage system,
which provides in-memory caching with LRU eviction and expiration for high-performance access.
"""

import logging
import time
from true_storage.storage.hot import HotStorage

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

    print("🚀 Initializing hot storage...")
    # Initialize with a small max size and short expiration time for demonstration
    storage = HotStorage(max_size=5, expiration_time=10)

    # Performance demonstration
    print("\n⚡ Performance comparison...")

    @measure_time
    def store_data():
        """Store sample data."""
        for i in range(10):
            key = f"key_{i}"
            value = {"data": f"value_{i}", "size": i * 100}
            storage.store(key, value)
            print(f"Stored {key}")

    @measure_time
    def retrieve_data_first_time():
        """First retrieval."""
        results = []
        for i in range(10):
            key = f"key_{i}"
            value = storage.retrieve(key)
            results.append(value)
            print(f"Retrieved {key}: {value}")
        return results

    print("\n💾 Storing sample data...")
    store_data()

    print("\n📊 Current storage stats:")
    stats = storage.get_stats()
    print(f"Storage size: {stats['size']} items")
    print(f"Max size: {stats['max_size']} items")
    print(f"Hit ratio: {stats['hit_ratio']:.2%}")
    print(f"Average response time: {stats['avg_response_time']:.2f}ms")

    print("\n🔍 Retrieving data...")
    results = retrieve_data_first_time()

    # Demonstrate LRU eviction
    print("\n🔄 Demonstrating LRU eviction...")
    print("Adding more items than max_size to trigger eviction...")
    for i in range(10, 15):
        key = f"key_{i}"
        value = {"data": f"value_{i}", "size": i * 100}
        storage.store(key, value)
        print(f"Stored {key}")

    print("\nChecking which items remain in storage:")
    remaining_keys = storage.get_keys()
    print(f"Remaining keys: {remaining_keys}")
    
    # Demonstrate expiration
    print("\n⏰ Demonstrating expiration...")
    print("Waiting for items to expire...")
    time.sleep(11)  # Wait longer than expiration_time
    
    print("\nTrying to retrieve expired items:")
    for key in remaining_keys:
        value = storage.retrieve(key)
        print(f"Retrieving {key}: {'Found' if value else 'Expired'}")

    # Final statistics
    print("\n📊 Final storage stats:")
    stats = storage.get_stats()
    print(f"Storage size: {stats['size']} items")
    print(f"Hit ratio: {stats['hit_ratio']:.2%}")
    print(f"Total operations: {stats['total_operations']}")
    print(f"Average response time: {stats['avg_response_time']:.2f}ms")

if __name__ == "__main__":
    main()
