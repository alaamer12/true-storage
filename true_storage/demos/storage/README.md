# True Storage Storage Demos 🗄️

This directory contains demonstration files showcasing the various storage backends and features of True Storage's storage module.

## Demo Files

1. `02_hot_storage.py` - Hot storage operations 🔥
   - In-memory caching
   - Performance optimization
   - Cache invalidation

2. `03_cold_storage.py` - Cold storage features ❄️
   - Long-term storage
   - Archival operations
   - Data compression

3. `04_mixed_storage.py` - Mixed storage strategies 🔄
   - Hot/Cold tiered storage
   - Automatic data migration
   - Access pattern optimization

## Features Demonstrated

- Storage initialization and configuration
- Data persistence and retrieval
- Cache management
- Performance optimization
- Error handling and recovery
- Data compression and archival
- Tiered storage strategies
- Automatic data migration
- Access pattern analysis

## Usage

Each demo can be run independently to showcase different aspects of the storage system:

```bash
python 01_basic_storage.py  # Basic operations
python 02_hot_storage.py    # Hot storage features
python 03_cold_storage.py   # Cold storage features
python 04_mixed_storage.py  # Mixed storage strategies
```

## Notes

- Hot storage demos use in-memory storage for fast access
- Cold storage demos create temporary directories for demonstration
- Mixed storage demos show automatic tiering between hot and cold storage
- All demos include proper cleanup of temporary resources
