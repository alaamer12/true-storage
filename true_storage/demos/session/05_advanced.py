"""
Advanced Session Features Demo

This demo showcases advanced features of the True Storage session management system.
"""

import threading
import time
import logging
from datetime import datetime
from true_storage.session import SessionStore, SessionStoreConfig

class SessionMonitor:
    """Utility class to monitor session store metrics."""
    
    def __init__(self, store: SessionStore):
        self.store = store
        self.start_time = time.time()
        self._stop_monitor = threading.Event()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
    
    def _monitor_loop(self):
        while not self._stop_monitor.is_set():
            active_sessions = len(self.store)
            total_accesses = sum(
                metadata.access_count
                for metadata in self.store._metadata.values()
            )
            print(f"\n📊 Monitor Stats ({datetime.now().strftime('%H:%M:%S')})")
            print(f"Active Sessions: {active_sessions}")
            print(f"Total Accesses: {total_accesses}")
            print(f"Uptime: {int(time.time() - self.start_time)} seconds")
            self._stop_monitor.wait(5)
    
    def stop(self):
        self._stop_monitor.set()
        self._monitor_thread.join()

def session_worker(name: str, store: SessionStore):
    """Worker function that performs various session operations."""
    for i in range(5):
        try:
            # Create a session
            key = f"worker_{name}_session_{i}"
            store.set(key, {
                'worker': name,
                'iteration': i,
                'timestamp': time.time()
            })
            
            # Simulate some work
            time.sleep(0.5)
            
            # Access the session
            data = store.get(key)
            if data:
                # Modify the session
                data['accessed'] = True
                store.set(key, data)
            
            # Sometimes lock the session
            if i % 2 == 0:
                store.lock(key, duration=1)
                time.sleep(0.5)
                store.unlock(key)
            
        except Exception as e:
            logging.error(f"Worker {name} error: {e}")

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Initialize session store with advanced configuration
    print("🚀 Initializing session store with advanced features...")
    config = SessionStoreConfig(
        max_size=1000,
        expiration_time=30,
        cleanup_interval=5,
        enable_logging=True,
        log_level=logging.INFO
    )
    store = SessionStore(config)
    
    # Start session monitoring
    print("\n📈 Starting session monitoring...")
    monitor = SessionMonitor(store)
    
    # Create worker threads
    print("\n👥 Starting worker threads...")
    workers = []
    for i in range(3):
        worker = threading.Thread(
            target=session_worker,
            args=(f"Worker-{i}", store)
        )
        workers.append(worker)
        worker.start()
    
    # Demonstrate metadata tracking
    print("\n📊 Demonstrating metadata tracking...")
    test_key = 'metadata_test'
    store.set(test_key, 'test_value')
    
    # Access the value multiple times
    for _ in range(5):
        store.get(test_key)
        time.sleep(0.1)
    
    # Display metadata
    if metadata := store.get_metadata(test_key):
        print(f"\nSession Metadata for '{test_key}':")
        print(f"Created: {datetime.fromtimestamp(metadata.created_at)}")
        print(f"Last Accessed: {datetime.fromtimestamp(metadata.last_accessed)}")
        print(f"Access Count: {metadata.access_count}")
        print(f"Status: {metadata.status}")
    
    # Demonstrate session status transitions
    print("\n🔄 Demonstrating session status transitions...")
    status_key = 'status_test'
    store.set(status_key, 'initial_value')
    
    print(f"Initial status: {store.get_status(status_key)}")
    
    store.lock(status_key)
    print(f"After lock: {store.get_status(status_key)}")
    
    store.unlock(status_key)
    print(f"After unlock: {store.get_status(status_key)}")
    
    # Wait for workers to complete
    print("\n⏳ Waiting for workers to complete...")
    for worker in workers:
        worker.join()
    
    # Final statistics
    print("\n📈 Final Statistics:")
    print(f"Total Sessions: {len(store)}")
    print("Session Keys:", list(store.keys()))
    
    # Stop monitoring and cleanup
    print("\n🛑 Stopping services...")
    monitor.stop()
    store.stop()

if __name__ == '__main__':
    main()
