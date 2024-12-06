"""Test suite for the environment management system.

This test suite focuses on core functionality of the environment management system:
- Basic environment operations
- Mode-specific functionality
- Environment snapshots
- Variable validation
- Environment inheritance
"""

import pytest
from pathlib import Path

from true_storage.env import (
    Environment,
    MODES,
    EnvError,
    ValidationError,
    ModeError,
    EnvValidator
)

# Fixtures
@pytest.fixture
def basic_env():
    """Basic environment fixture with some preset variables."""
    env = Environment()
    env.set('APP_NAME', 'TestApp')
    env.set('VERSION', '1.0.0')
    return env

@pytest.fixture
def mode_env():
    """Environment fixture with mode-specific variables."""
    env = Environment()
    env.set('DB_URL', 'localhost:5432', modes=[MODES.DEV, MODES.TEST])
    env.set('API_KEY', 'test-key-123', modes=[MODES.TEST])
    env.set('PROD_SECRET', 'secret-123', modes=[MODES.PROD])
    env.set('APP_NAME', 'TestApp', modes=[MODES.ALL])
    return env

@pytest.fixture
def validated_env():
    """Environment fixture with validation schema."""
    schema = {
        'PORT': int,
        'DEBUG': bool,
        'APP_NAME': str
    }
    return Environment(validator=EnvValidator(schema))

# Test Basic Environment Operations
def test_basic_operations(basic_env):
    """Test basic environment variable operations."""
    # Test getting existing variables
    assert basic_env.get('APP_NAME') == 'TestApp'
    assert basic_env.get('VERSION') == '1.0.0'
    
    # Test getting non-existent variable with default
    assert basic_env.get('UNDEFINED', 'default') == 'default'
    
    # Test dictionary-style access
    basic_env['DEBUG'] = 'true'
    assert basic_env['DEBUG'] == 'true'
    
    # Test variable deletion
    del basic_env['DEBUG']
    assert 'DEBUG' not in basic_env

def test_environment_length(basic_env):
    """Test environment length calculation."""
    initial_len = len(basic_env)
    basic_env.set('NEW_VAR', 'value')
    assert len(basic_env) == initial_len + 1

# Test Mode-Specific Functionality
def test_mode_specific_access(mode_env):
    """Test mode-specific variable access."""
    # Test DEV mode access
    with mode_env.with_mode(MODES.DEV):
        assert mode_env.get('APP_NAME') == 'TestApp'  # ALL mode
        assert mode_env.get('DB_URL') == 'localhost:5432'  # DEV mode
        with pytest.raises(ModeError):
            mode_env.get('API_KEY')  # TEST mode only
    
    # Test TEST mode access
    with mode_env.with_mode(MODES.TEST):
        assert mode_env.get('DB_URL') == 'localhost:5432'  # TEST mode
        assert mode_env.get('API_KEY') == 'test-key-123'  # TEST mode
    
    # Test PROD mode access
    with mode_env.with_mode(MODES.PROD):
        assert mode_env.get('PROD_SECRET') == 'secret-123'  # PROD mode
        with pytest.raises(ModeError):
            mode_env.get('DB_URL')  # DEV/TEST mode only

def test_mode_decorator(mode_env):
    """Test mode-specific decorator functionality."""
    @mode_env.mark(MODES.TEST)
    def test_function():
        return mode_env.get('API_KEY')
    
    with mode_env.with_mode(MODES.TEST):
        assert test_function() == 'test-key-123'
    
    with mode_env.with_mode(MODES.DEV):
        with pytest.raises(ModeError):
            test_function()

# Test Environment Snapshots
def test_snapshots(basic_env):
    """Test environment snapshot and rollback functionality."""
    # Create initial snapshot
    snapshot = basic_env.create_snapshot()
    
    # Modify environment
    basic_env.set('NEW_VAR', 'test')
    basic_env.set('APP_NAME', 'ModifiedApp')
    
    # Verify modifications
    assert basic_env.get('NEW_VAR') == 'test'
    assert basic_env.get('APP_NAME') == 'ModifiedApp'
    
    # Rollback and verify
    basic_env.rollback(snapshot)
    assert 'NEW_VAR' not in basic_env
    assert basic_env.get('APP_NAME') == 'TestApp'

# Test Variable Validation
def test_validation(validated_env):
    """Test environment variable validation."""
    # Test valid values
    validated_env.set('PORT', '8080')  # Should convert to int
    validated_env.set('DEBUG', 'true')  # Should convert to bool
    validated_env.set('APP_NAME', 'TestApp')
    
    assert isinstance(validated_env.get('PORT'), int)
    assert isinstance(validated_env.get('DEBUG'), bool)
    assert isinstance(validated_env.get('APP_NAME'), str)
    
    # Test invalid values
    with pytest.raises(ValidationError):
        validated_env.set('PORT', 'invalid_port')

# Test Environment Inheritance
def test_environment_inheritance():
    """Test environment inheritance functionality."""
    parent_env = Environment()
    parent_env.set('PARENT_VAR', 'parent_value')
    parent_env.set('SHARED_VAR', 'parent_value')
    
    child_env = Environment(parent=parent_env)
    child_env.set('CHILD_VAR', 'child_value')
    child_env.set('SHARED_VAR', 'child_value')  # Override parent
    
    # Test variable access
    assert child_env.get('PARENT_VAR') == 'parent_value'  # Inherited
    assert child_env.get('CHILD_VAR') == 'child_value'    # Own
    assert child_env.get('SHARED_VAR') == 'child_value'   # Overridden

# Test Environment Filtering
def test_environment_filtering(mode_env):
    """Test environment variable filtering functionality."""
    # Filter by key
    filtered = mode_env.filter('API')
    assert 'API_KEY' in filtered
    assert 'APP_NAME' not in filtered
    
    # Filter by value
    filtered = mode_env.filter('localhost', search_in='value')
    assert 'DB_URL' in filtered
    
    # Test predicate filtering
    def custom_filter(key, value):
        return key.startswith('APP_') and value == 'TestApp'
    
    filtered = mode_env.filter_with_predicate(custom_filter)
    assert 'APP_NAME' in filtered
