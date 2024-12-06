# True Storage Database Demos 🗄️

This directory contains demonstration files showcasing the various database backends and features of True Storage's database module.

## Demo Files

1. `01_basic_sqlite.py` - Basic SQLite operations and configuration 📝
   - Database creation and connection
   - Basic CRUD operations
   - Query execution

2. `02_filesystem_store.py` - File-based storage operations 📂
   - File-based data storage
   - Directory structure management
   - File operations and persistence

3. `03_redis_operations.py` - Redis backend functionality 🚀
   - Redis connection setup
   - Key-value operations
   - Caching and expiration

## Usage

Each demo file can be run independently. Make sure you have the required dependencies installed:

```bash
pip install redis  # For Redis demos
```

For Redis demos, ensure you have a Redis server running locally or update the connection settings accordingly.

## Notes

- SQLite demos use an in-memory database by default
- Filesystem demos create temporary directories for demonstration
- Redis demos require a running Redis server
- Each demo includes error handling and cleanup
