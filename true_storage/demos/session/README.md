# 🔄 Session Management Demos

This directory contains a series of demos showcasing True Storage's session management capabilities, from basic usage to advanced features.

## 📚 Demo Files

### 🔰 1. Basic Session Management (`01_basic_session.py`)

Demonstrates fundamental session operations:
- Session store initialization
- Setting and getting values
- Default values
- Dictionary-style access
- Basic session information

### 🕒 2. Expiration and Cleanup (`02_expiration.py`)

Shows session expiration and cleanup features:
- Custom expiration times
- Automatic cleanup
- Manual cleanup
- Session validation
- Expiration callbacks

### 🔒 3. Session Locking (`03_locking.py`)

Illustrates session locking capabilities:
- Exclusive access to sessions
- Lock timeouts
- Lock status checking
- Lock release
- Error handling

### 💾 4. Persistence and Recovery (`04_persistence.py`)

Explores session persistence features:
- Session persistence configuration
- Automatic backups
- Session recovery
- Atomic file operations
- Error handling

### 📊 5. Advanced Features (`05_advanced.py`)

Demonstrates advanced functionality:
- Session metadata tracking
- Custom eviction strategies
- Event logging
- Performance monitoring
- Multi-threading scenarios

## 🚀 Usage

Each demo can be run independently. To run a specific demo:

```bash
# Run basic session demo
python 01_basic_session.py

# Run expiration demo
python 02_expiration.py

# Run locking demo
python 03_locking.py

# Run persistence demo
python 04_persistence.py

# Run advanced features demo
python 05_advanced.py
```

## 📝 Notes

- Some demos create temporary files for persistence
- Cleanup is automatic but can be manually triggered
- Check comments in each file for specific requirements
- Some demos use multiple threads to demonstrate concurrency

## 🔗 Related Documentation

- [Session Module Documentation](https://true-storage.readthedocs.io/en/latest/modules/session.html)
- [API Reference](https://true-storage.readthedocs.io/en/latest/api_reference.html)
- [Main Project README](../../../../README.md)
