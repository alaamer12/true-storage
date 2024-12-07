"""Test suite for the environment management system.

This test suite focuses on core functionality of the environment management system:
- Basic environment operations
- Mode-specific functionality
- Environment snapshots
- Variable validation
- Environment inheritance
"""

import pytest
import os

from true_storage.env import (
    Environment,
    MODES,
    ValidationError,
    ModeError,
    EnvValidator,
    to_settings
)

# Fixtures
@pytest.fixture(scope="function")
def basic_env():
    """Basic environment fixture with some preset variables."""
    env = Environment()
    env.set({'APP_NAME': 'TestApp'})
    env.set({'VERSION': '1.0.0'})
    return env

@pytest.fixture(scope="function")
def mode_env():
    """Environment fixture with mode-specific variables."""
    env = Environment()
    env.set({'DB_URL': 'localhost:5432'}, modes=[MODES.DEV, MODES.TEST])
    env.set({'API_KEY': 'test-key-123'}, modes=[MODES.TEST])
    env.set({'PROD_SECRET': 'secret-123'}, modes=[MODES.PROD])
    env.set({'APP_NAME': 'TestApp'}, modes=[MODES.ALL])
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
    basic_env.set({'NEW_VAR': 'value'})
    assert len(basic_env) == initial_len + 1

# Test Mode-Specific Functionality
def test_mode_specific_access(mode_env):
    """Test mode-specific variable access."""
    # Test DEV mode access
    mode_env.mode = MODES.DEV
    assert mode_env.get('APP_NAME') == 'TestApp'  # ALL mode
    assert mode_env.get('DB_URL') == 'localhost:5432'  # DEV mode
    with pytest.raises(ModeError):
        mode_env.get('API_KEY')  # TEST mode only

    # Test TEST mode access
    mode_env.mode = MODES.TEST
    assert mode_env.get('DB_URL') == 'localhost:5432'  # TEST mode
    assert mode_env.get('API_KEY') == 'test-key-123'  # TEST mode

    # Test PROD mode access
    mode_env.mode = MODES.PROD
    assert mode_env.get('PROD_SECRET') == 'secret-123'  # PROD mode
    with pytest.raises(ModeError):
        mode_env.get('DB_URL')  # DEV/TEST mode only

def test_mode_decorator(mode_env):
    """Test mode-specific decorator functionality."""
    # Test function that requires TEST mode
    @mode_env.mark(MODES.TEST)
    def get_test_config():
        return mode_env.get('API_KEY')

    # Test function that requires PROD mode
    @mode_env.mark(MODES.PROD)
    def get_prod_secret():
        return mode_env.get('PROD_SECRET')

    # Execute in TEST mode
    mode_env.mode = MODES.TEST
    f = get_test_config()
    assert f == 'test-key-123'

    # Execute in PROD mode
    mode_env.mode = MODES.PROD
    assert get_prod_secret() == 'secret-123'

    # Execute in wrong mode
    mode_env.mode = MODES.DEV
    with pytest.raises(ModeError):
        f = get_test_config()  # Should fail in DEV mode

    with pytest.raises(ModeError):
        get_prod_secret()  # Should also fail in DEV mode

# Test Environment Snapshots
# noinspection PyUnusedLocal
def test_snapshots(basic_env):
    """Test environment snapshot and rollback functionality."""
    # Create initial state
    initial_vars = dict(basic_env.variables)

    # Modify environment
    basic_env.set({'NEW_VAR': 'test'})
    basic_env.set({'APP_NAME': 'ModifiedApp'})

    # Verify modifications
    assert basic_env.get('NEW_VAR') == 'test'
    assert basic_env.get('APP_NAME') == 'ModifiedApp'

    # Create snapshot after modifications
    snapshot = basic_env.create_snapshot()

    # Make more changes
    basic_env.set({'ANOTHER_VAR': 'value'})

    # Rollback and verify we're back to the snapshot state
    basic_env.rollback(snapshot)
    assert basic_env.get('NEW_VAR') == 'test'
    assert basic_env.get('APP_NAME') == 'ModifiedApp'
    assert 'ANOTHER_VAR' not in basic_env

# Test Variable Validation
def test_validation():
    """Test environment variable validation."""
    schema = {
        'PORT': int,
        'DEBUG': bool,
        'HOST': str,
    }
    env = Environment(validator=EnvValidator(schema))
    # Set test environment variables
    env.set({
        'PORT': '8080',
        'DEBUG': 'true',
        'HOST': 'localhost'
    })

    # Test valid types
    assert isinstance(env['PORT'], str)  # Original value is preserved
    assert isinstance(env['DEBUG'], str)
    assert isinstance(env['HOST'], str)

    # Test invalid types

    with pytest.raises(ValidationError):
        env['PORT'] = 'invalid'

# Test Environment Inheritance
def test_environment_inheritance():
    """Test environment inheritance functionality."""
    parent_env = Environment()
    parent_env.set({'PARENT_VAR': 'parent_value'})
    parent_env.set({'SHARED_VAR': 'parent_value'})

    child_env = Environment(parent=parent_env)
    child_env.set({'CHILD_VAR': 'child_value'})
    child_env.set({'SHARED_VAR': 'child_value'})  # Override parent

    # Test variable access
    assert child_env.get('PARENT_VAR') == 'parent_value'  # Inherited
    assert child_env.get('CHILD_VAR') == 'child_value'    # Own
    assert child_env.get('SHARED_VAR') == 'child_value'   # Overridden

# Test Environment Filtering
def test_environment_filtering():
    """Test environment variable filtering."""
    env = Environment(mode=MODES.DEV)
    env.set({
        'APP_NAME': 'test-app',
        'APP_VERSION': '1.0.0',
        'DEV_DB_URL': 'dev-db',
        'PROD_DB_URL': 'prod-db',
        'TEST_DB_URL': 'test-db',
        'SECRET_KEY': 'secret'
    })

    # Test basic filtering
    app_vars = env.filter_with_predicate(
        lambda k, _: k.startswith('APP_'),
        exclude_secrets=True
    )
    assert len(app_vars) == 2
    assert 'APP_NAME' in app_vars
    assert 'APP_VERSION' in app_vars

    # Test mode-specific filtering
    db_vars = env.filter_with_predicate(
        lambda k, _: k.endswith('DB_URL'),
        mode_specific=True
    )
    # FIXIT: TODO:
    # assert len(db_vars) == 1
    # assert 'DB_URL' in db_vars
    # assert db_vars['DB_URL'] == 'dev-db'
    #
    # # Test secret exclusion
    # all_vars = env.filter_with_predicate(lambda k, _: True, exclude_secrets=False)
    # assert 'SECRET_KEY' in all_vars
    #
    # filtered_vars = env.filter_with_predicate(lambda k, _: True, exclude_secrets=True)
    # assert 'SECRET_KEY' not in filtered_vars

# Test Pydantic Settings Conversion
# def test_pydantic_settings_conversion():
#     """Test conversion to pydantic_settings BaseSettings."""
#     from pydantic_settings import BaseSettings, SettingsConfigDict
#
#     # Set up test environment
#     os.environ.update({
#         'APP_NAME': 'TestApp',
#         'PORT': '8080',
#         'DEBUG': 'true',
#         'API_KEY': 'secret123'
#     })
#
#     class MySettings(BaseSettings):
#         app_name: str
#         port: int
#         debug: bool
#         api_key: str = 'default'
#
#         model_config = SettingsConfigDict(
#             env_file=None,
#             env_prefix='',
#             case_sensitive=False
#         )
#
#     # Create Environment instance
#     env = Environment()
#     env.set({'APP_NAME': 'TestApp'}, modes=[MODES.ALL])
#
#     # Convert to pydantic settings
#     settings = to_settings(env, MySettings)
#
#     # Test type conversion
#     assert isinstance(settings.port, int)
#     assert isinstance(settings.debug, bool)
#     assert isinstance(settings.app_name, str)
#
#     # Test values
#     assert settings.app_name == 'TestApp'
#     assert settings.port == 8080
#     assert settings.debug is True
#     assert settings.api_key == 'secret123'
