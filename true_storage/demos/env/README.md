# Environment Management Demos

This directory contains a series of demos showcasing the True Storage environment management system's capabilities, from basic usage to advanced features.

## Demo Files

### 1. Basic Environment Management (`01_basic_env.py`)
Demonstrates fundamental environment operations:
- Environment initialization
- Setting and getting variables
- Default values
- Dictionary-style access
- Basic environment information

### 2. Mode-Specific Operations (`02_mode_specific.py`)
Shows mode-aware environment management:
- Setting mode-specific variables
- Mode-based access control
- Mode switching with context managers
- Mode-specific decorators
- Mode validation and restrictions

### 3. Snapshots and State Management (`03_snapshots.py`)
Illustrates state management capabilities:
- Creating environment snapshots
- Rolling back to previous states
- Managing multiple configurations
- Timestamp-based snapshot tracking
- Configuration switching

### 4. Advanced Features (`04_advanced.py`)
Explores advanced functionality:
- Custom mode creation
- Variable filtering and pattern matching
- Complex mode-based operations
- Multi-mode configuration management
- Environment state inheritance

## Usage

Each demo can be run independently. To run a specific demo:

```bash
python -m true_storage.demos.env.01_basic_env
python -m true_storage.demos.env.02_mode_specific
python -m true_storage.demos.env.03_snapshots
python -m true_storage.demos.env.04_advanced
```

## Key Features Demonstrated

1. **Mode Support**
   - Development, Testing, Staging, Production modes
   - Custom mode creation
   - Mode-specific variable access
   - Mode switching and inheritance

2. **Variable Management**
   - Mode-specific variables
   - Universal variables (ALL mode)
   - Secure variable storage
   - Pattern-based variable filtering

3. **State Management**
   - Environment snapshots
   - State rollback
   - Configuration profiles
   - Timestamp tracking

4. **Access Control**
   - Mode-based restrictions
   - Secure mode mappings
   - Variable visibility rules
   - Mode validation

5. **Developer Tools**
   - Context managers
   - Decorators
   - Dictionary-style access
   - Configuration utilities

## Best Practices

1. **Mode Usage**
   - Use `MODES.ALL` for variables that should be accessible everywhere
   - Restrict sensitive variables to appropriate modes
   - Use context managers for temporary mode switches

2. **State Management**
   - Create snapshots before major changes
   - Use rollback for recovery
   - Maintain separate configurations per mode

3. **Security**
   - Never expose sensitive variables in development mode
   - Use mode restrictions for security-critical variables
   - Validate mode access before variable retrieval

4. **Configuration**
   - Group related variables
   - Use consistent naming patterns
   - Document mode requirements
   - Implement proper error handling

## Example Workflow

```python
from true_storage.env import Environment, MODES

# Initialize environment
env = Environment()

# Set mode-specific variables
env.set('DB_URL', 'localhost:5432', modes=[MODES.DEV, MODES.TEST])
env.set('API_KEY', 'secret-key', modes=[MODES.PROD])

# Create a snapshot
snapshot = env.create_snapshot()

# Switch modes and access variables
with env.with_mode(MODES.PROD):
    api_key = env.get('API_KEY')  # Works in PROD mode
    
# Rollback if needed
env.rollback(snapshot)
```

These demos provide a comprehensive overview of the environment management system's capabilities and serve as a reference for implementing environment-aware applications.
