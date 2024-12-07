"""Advanced environment configuration and management.

This module provides comprehensive control over environment variables.

Classes:
    Environment: Main class for managing environment configurations.
    MODES: Enum defining operational modes for environment management.

Functions:
    to_settings: Converts Environment instance to pydantic_settings v2 BaseSettings.

Types:
    EnvPath: Union type for environment file paths.

Exceptions:
    EnvError: Base exception for environment errors.
    ValidationError: Exception raised for environment validation errors.
    ModeError: Exception raised for mode-related errors.

Key Features:
    - Multiple environment sources (env files, JSON, config files)
    - Environment validation and type checking
    - Secure secret management
    - Environment inheritance and layering
    - Variable interpolation
    - Environment snapshots and rollback
    - Mode-specific environment variables
"""

import configparser
import contextlib
import functools
import json
import os
import threading
import time
import warnings
from pathlib import Path
from typing import (Any, Dict, Callable, Literal,
                    NoReturn, Union, Optional, Type,
                    TypeVar, Protocol, Set, List)
import enum
import dotenv

__all__ = [
    # Classes
    'Environment',

    # Enums
    'MODES',
    'EnvValidator',

    # Exceptions
    'EnvError',
    'ValidationError',
    'ModeError',

    # Functions
    'to_settings',
]

def __dir__() -> List[str]:
    return sorted(__all__)

T = TypeVar('T')
F = TypeVar('F', bound=Callable)
EnvPath = Union[os.PathLike, Dict, NoReturn, Path]

try:
    from pydantic_settings import BaseSettings
except ImportError:
    class BaseSettings:
        ...


# Store custom stages in a module-level dictionary
_custom_stages = {}

# TODO
class EnvStore:
    pass
class EnvError(Exception):
    """Exception raised for environment errors."""
    pass


class ValidationError(EnvError):
    """Exception raised for environment validation errors."""
    pass


class ModeError(EnvError):
    """Exception raised for mode-related errors."""
    pass


class MODES(str, enum.Enum):
    """Environment modes for configuration management.

    This enum defines different operational modes for environment variable management,
    each with specific behaviors and access patterns.

    Attributes:
        ALL (str): Special mode for variables accessible across all modes.
        DEV (str): Development mode for local development environment.
        TEST (str): Testing mode for test environment.
        STAGE (str): Staging mode for pre-production environment.
        PROD (str): Production mode for live environment.
    """
    ALL = 'all'
    DEV = 'dev'
    TEST = 'test'
    STAGE = 'stage'
    PROD = 'prod'

    def __init__(self, value):
        self._value_ = value

    @classmethod
    def _generate_next_value_(cls, name, start, count, last_values):
        """Generate the next value for enum members."""
        return name.lower()

    @property
    def is_development(self) -> bool:
        """Check if the current mode is a development mode."""
        return self in (self.DEV, self.TEST)

    @property
    def is_production(self) -> bool:
        """Check if the current mode is production mode."""
        return self == self.PROD

    @property
    def is_all(self) -> bool:
        """Check if the current mode is ALL mode."""
        return self == self.ALL

    @property
    def prefix(self) -> str:
        """Get the prefix for environment variables in this mode."""
        if self.is_all:
            return ""
        value = self.value.upper() if isinstance(self.value, str) else self.value
        return f"{value}_"

    @property
    def suffix(self) -> str:
        """Get the suffix for environment variables in this mode."""
        if self.is_all:
            return ""
        value = self.value.upper() if isinstance(self.value, str) else self.value
        return f"_{value}"

    @classmethod
    def with_stages(cls, **new_stages: str) -> Type[enum.Enum]:
        """
        Create a new MODES enum with additional custom stages.

        Args:
              **new_stages: Keyword arguments of new stage names and their values

        Returns:
            A new MODES enum class with additional stages

        Raises:
            ValueError: If a stage name conflicts with existing stages
        """
        # Validate new stages
        for name in new_stages:
            name_upper = name.upper()
            if name_upper in cls.__members__ or name_upper in new_stages:
                raise ValueError(f"Stage '{name}' already exists")

        # Create a new enum class dynamically
        new_members = {**cls.__members__, **{
            name.upper(): value for name, value in new_stages.items()
        }}

        return enum.Enum(cls.__name__, new_members, type=str)

    @classmethod
    def get_stage(cls, name: str) -> 'MODES':
        """Get a stage by name.

        Args:
            name: Name of the stage to get

        Returns:
            Either a MODES enum member or a CustomStage instance

        Raises:
            ValueError: If stage doesn't exist
        """
        name = name.upper()
        if hasattr(cls, name):
            return getattr(cls, name)
        if name in _custom_stages:
            return _custom_stages[name]
        raise ValueError(f"Stage '{name}' does not exist")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.name}: {self.value}>"

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash(self.value)


class EnvValidatorProtocol(Protocol):
    """Protocol defining the interface for environment validators."""

    # noinspection PyUnusedLocal
    def __init__(self, schema: dict):
        ...

    def validate(self, key: str, value: Any) -> Any:
        ...

class ModedCallableCache:
    """Cache manager for mode-specific function mappings.
    
    Handles both persistent and in-memory caching of function-to-mode mappings.
    Persistent cache is used for previously seen functions, while in-memory cache
    is used for newly decorated functions in the current session.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                # Initialize instance attributes here
                cls._instance._memory_cache = {}
                cls._instance._cache_file = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    '.moded_cache'
                )
                cls._instance._persistent_cache = cls._instance._load_cache()
            return cls._instance

    def _load_cache(self) -> Dict[str, MODES]:
        """Load function mode mappings from persistent cache."""
        with contextlib.suppress(json.JSONDecodeError, ValueError, OSError):
            if os.path.exists(self._cache_file):
                with open(self._cache_file, 'r') as f:
                    return {k: MODES(v) for k, v in json.load(f).items()}
        return {}

    def _save_cache(self) -> None:
        """Save function mode mappings to persistent cache."""
        with contextlib.suppress(OSError):
            with open(self._cache_file, 'w') as f:
                json.dump({k: v.value for k, v in self._persistent_cache.items()}, f)

    def get_mode(self, func_key: str) -> Optional[MODES]:
        """Get mode for a function from either cache."""
        return self._memory_cache.get(func_key) or self._persistent_cache.get(func_key)

    def set_mode(self, func_key: str, mode: MODES) -> None:
        """Set mode for a function in both caches."""
        # Store in memory cache
        self._memory_cache[func_key] = mode
        # Store in persistent cache
        self._persistent_cache[func_key] = mode
        self._save_cache()

    def clear_memory_cache(self) -> None:
        """Clear the in-memory cache while preserving persistent cache."""
        self._memory_cache.clear()


class ModedCallable:
    """Wrapper for mode-specific function execution.
    
    This class wraps functions to ensure they only execute in specific modes.
    Uses ModedCallableCache to maintain both persistent and in-memory caches
    of function-to-mode mappings.
    """
    # Singleton cache manager
    _cache = ModedCallableCache()
    
    def __init__(self, env: 'Environment', mode: MODES):
        """Initialize the mode-specific function wrapper.
        
        Args:
            env (Environment): Environment instance to manage modes
            mode (MODES): Mode to restrict function execution to
        """
        self.env = env
        self.mode = mode
    
    def __call__(self, func: F) -> F:
        """Wrap the function to enforce mode restrictions.
        
        Args:
            func (F): Function to wrap with mode restrictions
            
        Returns:
            F: Wrapped function that enforces mode restrictions
        """
        # Generate unique key for the function
        func_key = f"{func.__module__}.{func.__qualname__}"
        
        # Store the function's mode in both caches
        self._cache.set_mode(func_key, self.mode)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the required mode from cache
            required_mode = self._cache.get_mode(func_key)
            if required_mode is None:
                raise ModeError(f"Function '{func.__name__}' has no mode restriction")
            
            # Check if we're in the correct mode
            if self.env.mode != required_mode:
                raise ModeError(
                    f"Function '{func.__name__}' can only be called in {required_mode} mode, "
                    f"current mode is {self.env.mode}"
                )
            return func(*args, **kwargs)
        return wrapper


class ModeContext:
    """Context manager for temporary mode changes."""

    def __init__(self, env: 'Environment', mode: MODES):
        self.env = env
        self.new_mode = mode
        self.previous_mode = None

    def __enter__(self):
        self.previous_mode = self.env.mode
        self.env.mode = self.new_mode
        return self.env

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.env.mode = self.previous_mode


class EnvValidator:
    """Environment validator for type checking and validation."""

    def __init__(self, schema: Dict[str, Type]):
        self.schema = schema

    def validate(self, key: str, value: Any) -> Any:
        """Validate a value against the schema.

        Args:
            key (str): Key to validate
            value (Any): Value to validate

        Returns:
            Any: Validated value

        Raises:
            ValidationError: If validation fails
        """
        if key not in self.schema:
            return value

        expected_type = self.schema[key]
        try:
            # Handle boolean values specially
            if expected_type is bool and isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            
            # Handle other types
            return expected_type(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid value for {key}: {value} is not of type {expected_type.__name__}") from e


class EnvSnapshot:
    """Environment snapshot for backup and rollback."""

    def __init__(self, variables: Dict[str, str], timestamp: float):
        self.variables = variables.copy()
        self.timestamp = timestamp

    def restore(self) -> None:
        """Restore environment variables from snapshot."""
        os.environ.clear()
        os.environ.update(self.variables)

    @property
    def age(self) -> float:
        """Get the age of the snapshot in seconds."""
        return time.time() - self.timestamp


class Environment:
    """Advanced environment configuration and management system.

    This class provides a comprehensive environment variable management system with
    features like mode-specific variables, secure storage, and variable validation.

    Attributes:
        _mode (MODES): Current environment mode.
        _instance (Environment): Singleton instance of the environment.
        _lock (threading.Lock): Thread lock for singleton pattern.
        _mode_vars (Dict[MODES, Set[str]]): Mode-specific variable tracking.
        _secure_mode_mappings (Dict[str, Set[MODES]]): Secure storage of mode mappings.

    Args:
        env_data (EnvPath, optional): Source of environment data. Defaults to ".env".
        validator (EnvValidatorProtocol, optional): Validator for environment variables.
        parent (Environment, optional): Parent environment for inheritance.
        interpolate (bool, optional): Enable variable interpolation. Defaults to True.
    """

    _mode: MODES = MODES.DEV
    _instance = None
    _lock = threading.Lock()
    _mode_vars: Dict[MODES, Set[str]] = {mode: set() for mode in MODES}
    _secure_mode_mappings: Dict[str, Set[MODES]] = {}  # Stores which modes a variable is valid for

    def __new__(cls, *args, **kwargs):
        """Implement thread-safe singleton pattern."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
            *extenal_envs,
            env_data: EnvPath = ".env",
            validator: Optional[EnvValidatorProtocol] = None,
            parent: Optional['Environment'] = None,
            interpolate: bool = True,
            mode: MODES = MODES.DEV,
    ):
        self._mode = mode
        if not hasattr(self, '_initialized'):
            self._env_data = self.__handle_env_path(env_data)
            self._validator = validator
            self._parent = parent
            self._interpolate = interpolate
            self._snapshots: List[EnvSnapshot] = []
            self._secret_keys: set[str] = set()
            self.load_env()
            self._initialized = True
            self._external_env: dict = self.validate_external_envs(extenal_envs)
            self.set(self._external_env)

    @property
    def envpath(self):
        return self._env_data

    @property
    def externalenvs(self):
        return self._external_env

    @staticmethod
    def __handle_env_path(env_path: str) -> Dict[str, str]:
        """Handle different types of environment path inputs."""
        if isinstance(env_path, (str, os.PathLike)):
            if not os.path.exists(env_path):
                raise EnvError(f"Environment file not found: {env_path}")
            return {"path": str(env_path)}
        elif isinstance(env_path, dict):
            return env_path
        else:
            raise EnvError(f"Invalid environment path type: {type(env_path)}")

    def _interpolate_value(self, value: str) -> str:
        """Interpolate environment variables in value."""
        if not self._interpolate or not isinstance(value, str):
            return value

        import re
        pattern = r'\${([^}]+)}'

        def replace(match):
            var_name = match.group(1)
            return os.environ.get(var_name, match.group(0))

        return re.sub(pattern, replace, value)

    def load_env(self) -> None:
        """Load environment variables with inheritance and interpolation."""
        try:
            # Load parent environment first if exists
            if self._parent:
                self._parent.load_env()

            # Load current environment
            if "path" in self._env_data:
                dotenv.load_dotenv(self._env_data["path"])
            else:
                for key, value in self._env_data.items():
                    interpolated_value = self._interpolate_value(str(value))
                    os.environ[key] = interpolated_value

            # Validate if validator is provided
            if self._validator:
                for key, value in os.environ.items():
                    self._validator.validate(key, value)

        except Exception as e:
            raise EnvError(f"Failed to load environment: {e}")

    def mark(self, mode: MODES) -> ModedCallable:
        """Decorator for mode-specific function execution.

        Args:
            mode (MODES): Mode to execute the function in.

        Returns:
            Callable: Decorated function that executes in specified mode.

        Example:
            >>> env = Environment()
            >>> @env.mark(MODES.TEST)
            ... def test_function():
            ...     return env.get('TEST_CONFIG')  # Only accessible in test mode
        """
        return ModedCallable(self, mode)

    def with_mode(self, mode: MODES) -> ModeContext:
        """Context manager for temporary mode switching.

        Args:
            mode (MODES): Mode to temporarily switch to.

        Yields:
            Environment: Self with temporarily changed mode.

        Example:
            >>> env = Environment()
            >>> with env.with_mode(MODES.PROD):
            ...     secret = env.get('API_KEY')  # Access production-only variable
        """
        return ModeContext(self, mode)

    def _is_mode_var(self, key: str, mode: Optional[MODES] = None) -> bool:
        """Check if a variable belongs to a specific mode."""
        if mode is None:
            mode = self.mode
        return (
                mode != MODES.ALL and (
                key.startswith(mode.prefix) or
                key.endswith(mode.suffix) or
                key in self._mode_vars[mode])
        )

    def mark_as_mode_var(self, key: str, mode: MODES) -> None:
        """Mark a variable as belonging to a specific mode."""
        self._mode_vars[mode].add(key)

    def _get_mode_key(self, key: str, mode: Optional[MODES] = None) -> str:
        """Generate a mode-specific key for an environment variable.

        Args:
            key (str): Base variable name.
            mode (MODES, optional): Mode to generate key for. Defaults to current mode.

        Returns:
            str: Mode-specific variable key.
        """
        mode = mode or self.mode
        if mode == MODES.ALL:
            return key
        return f"{mode.prefix}{key}"

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _get_base_key(key: str) -> str:
        """Extract the base key from a mode-specific key.

        Args:
            key (str): Mode-specific variable key.

        Returns:
            str: Base variable name without mode prefix/suffix.
        """
        for mode in MODES:
            if mode == MODES.ALL:
                continue
            if key.startswith(mode.prefix):
                return key[len(mode.prefix):]
            if key.endswith(mode.suffix):
                return key[:-len(mode.suffix)]
        return key

    def is_allowed_in_mode(self, key: str, mode: MODES) -> bool:
        """Check if a variable is allowed in a specific mode.

        Args:
            key (str): The variable name to check.
            mode (MODES): The mode to check against.

        Returns:
            bool: True if the variable is accessible in the specified mode, False otherwise.
        """
        if key not in self._secure_mode_mappings:
            return True  # If no mode restrictions, allowed in all modes
        return mode in self._secure_mode_mappings[key] or MODES.ALL in self._secure_mode_mappings[key]

    @staticmethod
    def create_snapshot() -> EnvSnapshot:
        """Create a snapshot of the current environment state.

        Returns:
            EnvSnapshot: Snapshot containing current variable values.

        Example:
            >>> env = Environment()
            >>> snapshot = env.create_snapshot()
            >>> env.set({'DEBUG': 'false'})
            >>> env.rollback(snapshot)  # Restore previous state
        """
        return EnvSnapshot(
            variables={k: v for k, v in os.environ.items()},
            timestamp=time.time()
        )

    @staticmethod
    def rollback(snapshot: EnvSnapshot) -> None:
        """Rollback environment to a previous snapshot.

        Args:
            snapshot (EnvSnapshot): Snapshot to restore from.

        Example:
            >>> env = Environment()
            >>> snapshot = env.create_snapshot()
            >>> env.set({'DEBUG': 'false'})
            >>> env.rollback(snapshot)  # Restore DEBUG to previous value
        """
        # Clear current environment
        os.environ.clear()
        # Restore variables from snapshot
        os.environ.update(snapshot.variables)

    def get(self, key: str, default: Any = None, mode: MODES = None,) -> str:
        """Retrieve an environment variable with mode support.

        Args:
            key (str): The variable name to retrieve.
            mode (MODES): To specify a mode or it will go for current mode.
            default (Any, optional): Default value if variable not found. Defaults to None.

        Returns:
            str: The value of the environment variable.

        Raises:
            ModeError: If the variable is not accessible in the current mode.
        """
        current_mode = mode or self.mode

        if key in self._secure_mode_mappings:
            allowed_modes = self._secure_mode_mappings[key]
            if MODES.ALL not in allowed_modes and current_mode not in allowed_modes:
                raise ModeError(f"Variable '{key}' is not accessible in mode {current_mode}")

        mode_key = self._get_mode_key(key)
        value = os.environ.get(mode_key)

        if value is None:
            value = os.environ.get(key, default)

        return value

    def set(self, items: Dict[str, Any], system_env: bool = False, modes: Optional[List[MODES]] = None) -> None:
        """Set environment variables with mode-specific access control."""
        modes = self._normalize_modes(modes) if modes else [MODES.ALL]

        for key, value in items.items():
            self._validate_and_set_value(key, value, system_env, modes)

    def _validate_and_set_value(self, key: str, value: Any, system_env: bool, modes: List[MODES]) -> None:
        """Validate and set a single environment variable."""
        value = self._validate_value(key, value)
        str_value = str(value)

        # Update secure mapping
        self._secure_mode_mappings[key] = set(modes)

        self._set_value_in_environments(key, str_value, system_env, modes)
        self._track_mode_variables(key, modes)

    def _validate_value(self, key: str, value: Any) -> Any:
        """Validate the value if a validator is present."""
        return self._validator.validate(key, value) if self._validator else value

    def _set_value_in_environments(self, key: str, value: str, system_env: bool, modes: List[MODES]) -> None:
        """Set the value in appropriate environments based on modes."""
        # First, remove any existing mode-specific values
        self._remove_mode_specific(key)
        
        # Then set the new value
        if MODES.ALL in modes:
            os.environ[key] = value
            self._env_data[key] = value
        else:
            for mode in modes:
                mode_key = self._get_mode_key(key, mode)
                os.environ[mode_key] = value
                self._env_data[mode_key] = value

    # noinspection PyTypeChecker
    def _remove_mode_specific(self, key):
        base_key = self._get_base_key(key)
        for mode in MODES:
            mode_key = self._get_mode_key(base_key, mode)
            if mode_key in os.environ:
                del os.environ[mode_key]
            if mode_key in self._env_data:
                del self._env_data[mode_key]

    def _track_mode_variables(self, key: str, modes: List[MODES]) -> None:
        """Track variables for each mode."""
        for mode in modes:
            if mode != MODES.ALL:
                self._mode_vars[mode].add(key)

    def delete(self, key: str, modes: Optional[List[MODES]] = None) -> None:
        """Delete an environment variable from specified modes.

        Args:
            key (str): The variable name to delete.
            modes (List[MODES], optional): List of modes to delete from.
                If None, deletes from all modes.

        Example:
            >>> env = Environment()
            >>> env.delete('DEBUG', modes=[MODES.PROD])  # Remove from production only
            >>> env.delete('API_KEY')  # Remove from all modes
        """
        modes = self._normalize_modes(modes)
        self._delete_from_env(key, modes)
        self._update_secure_mappings(key, modes)

    @staticmethod
    def _normalize_modes(modes: Optional[List[MODES]]) -> List[MODES]:
        """Normalize the modes list to handle None case.

        Args:
            modes (List[MODES], optional): List of modes to normalize.

        Returns:
            List[MODES]: All available modes if input is None, otherwise the input list.
        """
        return list(MODES) if modes is None else modes

    def _delete_from_env(self, key: str, modes: List[MODES]) -> None:
        """Delete the variable from specified modes in the environment.

        Args:
            key (str): The variable name to delete.
            modes (List[MODES]): List of modes to delete from.
        """
        for mode in modes:
            if mode == MODES.ALL:
                self._delete_common_variable(key)
            else:
                self._delete_mode_specific_variable(key, mode)

    @staticmethod
    def _delete_common_variable(key: str) -> None:
        """Delete a common (non-mode-specific) variable.

        Args:
            key (str): The variable name to delete.
        """
        if key in os.environ:
            del os.environ[key]

    def _delete_mode_specific_variable(self, key: str, mode: MODES) -> None:
        """Delete a mode-specific variable.

        Args:
            key (str): The variable name to delete.
            mode (MODES): The mode to delete from.
        """
        mode_key = self._get_mode_key(key, mode)
        if mode_key in os.environ:
            del os.environ[mode_key]

    def _update_secure_mappings(self, key: str, modes: List[MODES]) -> None:
        """Update the secure mode mappings after variable deletion.

        Args:
            key (str): The variable name that was deleted.
            modes (List[MODES]): The modes it was deleted from.
        """
        if key in self._secure_mode_mappings:
            self._secure_mode_mappings[key] -= set(modes)
            if not self._secure_mode_mappings[key]:
                del self._secure_mode_mappings[key]

    @property
    def mode_mappings(self) -> Dict[str, Set[MODES]]:
        """Get a secure copy of the mode-to-variable mappings.

        Returns:
            Dict[str, Set[MODES]]: A mapping of variable names to their allowed modes.
        """
        return self._secure_mode_mappings.copy()

    @property
    def variables(self) -> Dict[str, str]:
        """Get all environment variables."""
        return dict(os.environ)

    @property
    def secrets(self) -> Dict[str, str]:
        """Get all secret environment variables."""
        return {k: v for k, v in self.variables.items() if k in self._secret_keys}

    @property
    def non_secrets(self) -> Dict[str, str]:
        """Get all non-secret environment variables."""
        return {k: v for k, v in self.variables.items() if k not in self._secret_keys}

    @property
    def mode(self) -> MODES:
        """Get current environment mode."""
        return self._mode

    @mode.setter
    def mode(self, value: MODES) -> None:
        """Set environment mode."""
        self._mode = value

    @property
    def parent(self) -> Optional['Environment']:
        """Get parent environment."""
        return self._parent

    @property
    def snapshots(self) -> List[EnvSnapshot]:
        """Get list of environment snapshots."""
        return self._snapshots.copy()

    @property
    def mode_variables(self) -> Dict[str, str]:
        """Get all variables specific to the current mode.

        Returns:
            Dict[str, str]: Dictionary of mode-specific variables.
        """
        return {
            self._get_base_key(k): v
            for k, v in self.variables.items()
            if self._is_mode_var(k)
        }

    def __str__(self) -> str:
        """Get string representation of environment state.

        Returns:
            str: Human-readable environment information.
        """
        return (
            f"Environment(mode={self.mode}, "
            f"total_vars={len(self.variables)}, "
            f"secret_vars={len(self.secrets)}, "
            f"mode_vars={len(self.mode_variables)})"
        )

    def __getitem__(self, key: str) -> str:
        """Get environment variable using dictionary-style access with mode support."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set environment variable using dictionary-style access with mode support."""
        self.set({key: value})

    def __delitem__(self, key: str) -> None:
        """Delete environment variable using dictionary-style access with mode support."""
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        """Check if environment variable exists using 'in' operator with mode support."""
        mode_key = self._get_mode_key(key)
        return mode_key in os.environ or key in os.environ

    def __iter__(self):
        """Iterate over environment variables."""
        seen = set()
        for key in self.variables:
            base_key = self._get_base_key(key)
            if base_key not in seen:
                seen.add(base_key)
                yield base_key

    def __len__(self) -> int:
        """Get number of unique base environment variables."""
        return len(set(self._get_base_key(k) for k in self.variables))

    def filter(
            self,
            search_value: str,
            search_in: Literal["key", "value"] = "key",
            exclude_secrets: bool = True,
            mode_specific: bool = True
    ) -> Dict[str, str]:
        """Filter environment variables with mode and secret support."""
        env_vars = self.non_secrets if exclude_secrets else self.variables

        if mode_specific:
            env_vars = {
                self._get_base_key(k): v
                for k, v in env_vars.items()
                if self._is_mode_var(k)
            }

        if search_in == "key":
            return {k: v for k, v in env_vars.items() if search_value in k}
        else:
            return {k: v for k, v in env_vars.items() if search_value in v}

    def filter_with_predicate(
            self,
            predicate: Callable[[str, str], bool],
            exclude_secrets: bool = True,
            mode_specific: bool = True
    ) -> Dict[str, str]:
        """Filter environment variables with a predicate function."""
        # Get initial set of variables
        env_vars = self.non_secrets if exclude_secrets else self.variables

        # Apply mode-specific filtering if requested
        if mode_specific:
            # Keep only variables that are NOT mode-specific
            env_vars = {k: v for k, v in env_vars.items() if not self._is_mode_var(k)}

        # Apply the predicate to the filtered variables
        return {k: v for k, v in env_vars.items() if predicate(k, v)}

    @classmethod
    def from_json(cls, json_path: str, **kwargs) -> 'Environment':
        """Create an Environment instance from a JSON file."""
        try:
            with open(json_path, 'r') as f:
                env_data = json.load(f)
            return cls(env_data=env_data, **kwargs)
        except Exception as e:
            raise EnvError(f"Failed to load JSON environment file: {e}")

    @classmethod
    def from_dict(cls, env_dict: Dict[str, Any], **kwargs) -> 'Environment':
        """Create an Environment instance from a dictionary."""
        return cls(env_data=env_dict, **kwargs)

    @classmethod
    def from_config(cls, config_path: str, **kwargs) -> 'Environment':
        """Create an Environment instance from a configuration file."""
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            env_data = {
                key: value
                for section in config.sections()
                for key, value in config[section].items()
            }
            return cls(env_data=env_data, **kwargs)
        except Exception as e:
            raise EnvError(f"Failed to load config file: {e}")

    def validate_external_envs(self, extenal_envs: tuple):
        if not extenal_envs:
            return {}
        if "__ALL__" in extenal_envs:
            return os.environ
        else:
            return {_e : os.environ.get(_e) for _e in self._external_env}

    def write_env(self, env_path):
        ...
        # TODO: create to add all envs
        # envpath = env_path or self.envpath
        # with open(envpath, 'w'):
            # "=".join(k, v for k, v in self.da)


def to_settings(env_instance: 'Environment', settings_class: Type[BaseSettings]) -> BaseSettings:
    """Convert an Environment instance to a pydantic_settings v2 BaseSettings instance.

    This allows optional pydantic compatibility without modifying the core Environment class.

    Args:
        env_instance (Environment): The Environment instance to convert
        settings_class (Type[BaseSettings]): The pydantic_settings BaseSettings class to convert to

    Returns:
        BaseSettings: An instance of the provided BaseSettings class

    Example:
        >>> from pydantic_settings import BaseSettings, SettingsConfigDict # Recommended V2
        >>> from typing import Optional
        >>>
        >>> class MySettings(BaseSettings):
        ...     app_name: str
        ...     port: int
        ...     debug: bool = False
        ...     api_key: Optional[str] = None
        ...
        ...     model_config = SettingsConfigDict(
        ...         env_file='.env',
        ...         env_prefix='',
        ...         case_sensitive=False
        ...     )
        ...
        >>> env = Environment()
        >>> settings = to_settings(env, MySettings)
    """
    # Get all environment variables from the Environment instance
    env_vars = {
        k: v for k, v in os.environ.items()
        if env_instance.is_allowed_in_mode(k, env_instance.mode)
    }

    # Create settings instance with environment variables
    try:
        settings = settings_class.model_validate({
            "_env_file": env_instance.envpath.get("path", None),
            **env_vars
        })
    except ImportError as i:
        warnings.warn("Have you installed pydantic_settings")
        raise i
    except Exception as e:
        raise e
    else:
        return settings

def override():
    # TODO: to be comptaible with override method from `typing`.
    pass

if __name__ == "__main__":
    def main():
        """Test the Environment functionality."""
        print("\n=== Environment Management Demo ===\n")
        env_path = r"E:\Projects\Languages\Python\true-storage\.env"
        env = Environment(env_data=env_path)

        print("1. Basic Environment Setup")
        print("--------------------------")
        print(f"Current Mode: {env.mode}")
        print(f"Total Variables: {len(env)}")
        print(f"Mode Variables: {len(env.mode_variables)}")

        print("\n2. Setting Variables")
        print("-------------------")
        # Set variables with different mode access
        env.set({'APP_NAME': 'TrueStorage'}, modes=[MODES.ALL])  # Available in all modes
        env.set({'DB_URL': 'localhost:5432'}, modes=[MODES.DEV, MODES.TEST])  # Only in dev and test
        env.set({'API_KEY': 'test-key-123'}, modes=[MODES.TEST])  # Only in test
        env.set({'PROD_SECRET': 'secret-123'}, modes=[MODES.PROD])  # Only in production

        print("Variables after setting:")
        print(f"Mode mappings: {env.mode_mappings}")

        print("\n3. Mode-Specific Access")
        print("----------------------")
        # Test different modes
        for mode in [MODES.DEV, MODES.TEST, MODES.PROD]:
            with env.with_mode(mode):
                print(f"\nIn {mode.value.upper()} mode:")
                # Try accessing APP_NAME (should work in all modes)
                print(f"APP_NAME: {env.get('APP_NAME')}")

                # Try accessing mode-specific variables
                try:
                    print(f"DB_URL: {env.get('DB_URL')}")
                except ModeError as e:
                    print(f"DB_URL: {e}")

                try:
                    print(f"API_KEY: {env.get('API_KEY')}")
                except ModeError as e:
                    print(f"API_KEY: {e}")

                try:
                    print(f"PROD_SECRET: {env.get('PROD_SECRET')}")
                except ModeError as e:
                    print(f"PROD_SECRET: {e}")

        print("\n4. Decorator Usage")
        print("-----------------")

        @env.mark(MODES.TEST)
        def test_function():
            return f"Test DB URL: {env.get('DB_URL')}"

        @env.mark(MODES.PROD)
        def prod_function():
            return f"Production Secret: {env.get('PROD_SECRET')}"

        print(test_function())
        print(prod_function())

        print("\n5. Variable Filtering")
        print("-------------------")
        # Set some additional variables for filtering
        env.set({'DB_HOST': 'localhost'}, modes=[MODES.ALL])
        env.set({'DB_PORT': '5432'}, modes=[MODES.ALL])
        env.set({'APP_VERSION': '1.0.0'}, modes=[MODES.ALL])

        db_vars = env.filter('DB_', search_in='key')
        print(f"DB-related variables: {db_vars}")

        print("\n6. Snapshots")
        print("------------")
        # Create a snapshot
        snapshot = env.create_snapshot()
        print(f"Created snapshot at: {snapshot.timestamp}")

        # Change some variables
        env.set({'DB_URL': 'new-db:5432'}, modes=[MODES.DEV, MODES.TEST])
        print(f"After change - DB_URL: {env.get('DB_URL')}")

        # Rollback
        env.rollback(snapshot)
        print(f"After rollback - DB_URL: {env.get('DB_URL')}")

        print("\n7. Environment Info")
        print("-----------------")
        print(env)



    main()
