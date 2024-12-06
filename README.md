# 🚀 True Storage

[![PyPI version](https://badge.fury.io/py/true-storage.svg)](https://badge.fury.io/py/true-storage)
[![Documentation Status](https://readthedocs.org/projects/true-storage/badge/?version=latest)](https://true-storage.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python library for advanced storage management, environment configuration, and session handling.

## ✨ Features

### 🌍 Advanced Environment Management
- 📁 Multiple environment sources (env files, JSON, config files)
- 🔐 Environment validation and type checking
- 🔄 Mode-specific variables (dev, test, stage, prod)
- ⚡ Variable interpolation
- 📸 Environment snapshots and rollback
- 🔌 Optional Pydantic integration

### 🔄 Session Management
- 🔒 Thread-safe in-memory session store
- ⏰ Automatic expiration and cleanup
- 📊 LRU eviction strategy
- ⚙️ Configurable size and timeout

### 💾 Storage Solutions
- 🔥 Hot storage for frequently accessed data
- ❄️ Cold storage for archival data
- 🔄 Mixed storage strategy
- 🛠️ Base storage interface for custom implementations

### 🗄️ Database Integration
- 🔒 Thread-safe database implementations
- 📁 Filesystem storage with atomic operations
- 📦 Redis support with connection pooling
- 🎲 SQLite with BLOB storage optimization
- 🔄 Pickle-based serialization
- 🏷️ Customizable key prefixing
- ⚠️ Error handling and connection management

## 🚀 Installation

```bash
# Basic installation
pip install true-storage

# With Pydantic support
pip install true-storage[pydantic]
```

## 📚 Quick Start

### 🌍 Environment Management

```python
from true_storage.env import Environment, MODES

# Initialize environment
env = Environment(env_data=".env")

# Set mode-specific variables
env.set('API_KEY', 'secret-key', modes=[MODES.PROD])
env.set('DEBUG', 'true', modes=[MODES.DEV])

# Access variables with mode context
with env.with_mode(MODES.PROD):
    api_key = env.get('API_KEY')  # Only accessible in PROD mode
```

### 🔄 Session Management

```python
from true_storage.session import SessionStore, SessionStoreConfig

# Configure session store
config = SessionStoreConfig(
    max_size=1000,
    expiration_time=3600,  # 1 hour
    cleanup_interval=60    # 1 minute
)

# Initialize session store
store = SessionStore(config)

# Use session store
store.set('user_id', 'user123')
user_id = store.get('user_id')
```

### 💾 Storage Management

```python
from true_storage.storage.hot import HotStorage
from true_storage.storage.cold import ColdStorage
from true_storage.storage.mixed import MixedStorage

# Initialize storage
hot_storage = HotStorage()
cold_storage = ColdStorage()
mixed_storage = MixedStorage()

# Store and retrieve data
mixed_storage.store('key', 'value')
value = mixed_storage.retrieve('key')
```

### 🗄️ Database Integration

```python
# File System Storage
from true_storage.database import FileSystemStorage
fs_storage = FileSystemStorage(base_dir="/path/to/storage")
fs_storage.store("key", {"data": "value"})

# Redis Storage
from true_storage.database import RedisStorage
redis_storage = RedisStorage(host="localhost", port=6379, prefix="app:")
redis_storage.store("key", ["list", "of", "items"])

# SQLite Storage
from true_storage.database import SQLiteStorage
sqlite_storage = SQLiteStorage(db_path="app.db")
sqlite_storage.store("key", {"complex": "data"})
```

## 📖 Documentation

For detailed documentation, visit [true-storage.readthedocs.io](https://true-storage.readthedocs.io/).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.