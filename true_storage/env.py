"""Environment configuration and management."""

import configparser
import functools
import json
import os
from pathlib import Path
from typing import Any, Dict, Callable, Literal, NoReturn, Union

import dotenv

EnvPath = Union[os.PathLike, Dict, NoReturn, Path]

class EnvError(Exception):
    """Exception raised for environment errors."""
    pass

from enum import StrEnum


class MODES(StrEnum):
    """Environment modes."""
    DEV = 'dev'
    TEST = 'test'
    PROD = 'prod'


class Environment:
    """Environment configuration and management."""

    _mode: MODES = MODES.DEV

    def __init__(self, env_data: EnvPath = ".env"):
        self._env_data = self.__handle_env_path(env_data)
        self.load_env()

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

    def load_env(self) -> None:
        """Load environment variables."""
        try:
            if "path" in self._env_data:
                dotenv.load_dotenv(self._env_data["path"])
            else:
                for key, value in self._env_data.items():
                    os.environ[key] = str(value)
        except Exception as e:
            raise EnvError(f"Failed to load environment: {e}")

    def read_env(self) -> Dict[str, str]:
        """Read all environment variables."""
        return dict(os.environ)

    def set_env(self, key: str, value: Any) -> None:
        """Set an environment variable."""
        os.environ[key] = str(value)

    def get_env(self, key: str) -> str:
        """Get an environment variable."""
        value = os.getenv(key)
        if value is None:
            raise EnvError(f"Environment variable not found: {key}")
        return value

    def override_env(self, key: str, value: Any) -> None:
        """Override an environment variable."""
        self.set_env(key, value)

    def filter_env(
            self, search_value: str, search_in: Literal["key", "value"] = "key"
    ) -> Dict[str, str]:
        """Filter environment variables."""
        env_vars = self.read_env()
        if search_in == "key":
            return {k: v for k, v in env_vars.items() if search_value in k}
        else:
            return {k: v for k, v in env_vars.items() if search_value in v}

    def filter_with_predicate(
            self, predicate: Callable[[str, str], bool]
    ) -> Dict[str, str]:
        """Filter environment variables with a predicate function."""
        env_vars = self.read_env()
        return {k: v for k, v in env_vars.items() if predicate(k, v)}

    @classmethod
    def mode(cls, func_mode: MODES = MODES.TEST) -> Callable:
        """Decorator to set environment mode."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                previous_mode = cls._mode
                cls._mode = func_mode
                try:
                    return func(*args, **kwargs)
                finally:
                    cls._mode = previous_mode
            return wrapper
        return decorator

    @classmethod
    def from_json(cls, json_path: str) -> 'Environment':
        """Create an Environment instance from a JSON file."""
        try:
            with open(json_path, 'r') as f:
                env_data = json.load(f)
            return cls(env_data)
        except Exception as e:
            raise EnvError(f"Failed to load JSON environment file: {e}")

    @classmethod
    def from_dict(cls, env_dict: Dict[str, Any]) -> 'Environment':
        """Create an Environment instance from a dictionary."""
        return cls(env_dict)

    @classmethod
    def from_config(cls, config_path: str) -> 'Environment':
        """Create an Environment instance from a configuration file."""
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            env_data = {
                key: value
                for section in config.sections()
                for key, value in config[section].items()
            }
            return cls(env_data)
        except Exception as e:
            raise EnvError(f"Failed to load config file: {e}")

    def __repr__(self) -> str:
        return f"Environment(mode={self._mode}, vars={len(self.read_env())})"
