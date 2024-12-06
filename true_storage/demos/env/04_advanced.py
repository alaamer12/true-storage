"""Advanced environment management features demo.

This demo shows advanced functionality:
- Custom mode creation
- Variable filtering
- Mode inheritance
- Complex mode-based operations
"""

from true_storage.env import Environment, MODES


def main():
    """Demonstrate advanced environment functionality."""
    print("\n=== Advanced Environment Features Demo ===\n")

    env = Environment()

    # 1. Custom mode creation
    print("1. Custom Modes")
    print("   ------------")
    # Set variable in STAGE mode
    env.set('STAGE_URL', 'stage.example.com', modes=[MODES.STAGE])
    # Only show public modes (exclude those starting with _)
    available_modes = [mode.name for mode in MODES if not mode.name.startswith('_')]
    print(f"   Available Modes: {available_modes}")

    # Switch to STAGE mode to access the variable
    env.mode = MODES.STAGE
    print(f"   Current Mode: {env.mode}")
    print(f"   STAGE_URL: {env.get('STAGE_URL')}")

    # Switch back to DEV mode
    env.mode = MODES.DEV

    # 2. Variable filtering
    print("\n2. Variable Filtering")
    print("   -----------------")

    # Set up some variables
    env.set('DB_HOST', 'localhost', modes=[MODES.DEV])
    env.set('DB_PORT', '5432', modes=[MODES.DEV])
    env.set('DB_NAME', 'myapp', modes=[MODES.DEV])
    env.set('API_HOST', 'api.example.com', modes=[MODES.DEV])

    # Filter DB-related variables
    db_vars = {k: v for k, v in env.variables.items() if 'DB_' in k}
    print("   DB-related variables:")
    for key, value in db_vars.items():
        print(f"   - {key}: {value}")

    # 3. Mode-specific operations
    print("\n3. Mode-Specific Operations")
    print("   ----------------------")

    def get_connection_string(mode: MODES) -> str:
        with env.with_mode(mode):
            try:
                return f"postgresql://{env.get('DB_HOST')}:{env.get('DB_PORT')}/{env.get('DB_NAME')}"
            except Exception:
                return "Not configured for this mode"

    print(f"   DEV Connection: {get_connection_string(MODES.DEV)}")
    print(f"   PROD Connection: {get_connection_string(MODES.PROD)}")

    # 4. Complex Mode Handling
    print("\n4. Complex Mode Handling")
    print("   -------------------")

    # Set up mode-specific configurations
    env.mode = MODES.DEV
    env.set('DEBUG', 'true', modes=[MODES.DEV])
    env.set('LOG_LEVEL', 'DEBUG', modes=[MODES.DEV])
    env.set('CACHE_ENABLED', 'false', modes=[MODES.DEV])

    print("\n   DEV Configuration:")
    print(f"   - DEBUG: {env.get('DEBUG')}")
    print(f"   - LOG_LEVEL: {env.get('LOG_LEVEL')}")
    print(f"   - CACHE_ENABLED: {env.get('CACHE_ENABLED')}")

    # Switch to TEST mode and set up test configuration
    env.mode = MODES.TEST
    env.set('DEBUG', 'true', modes=[MODES.TEST])
    env.set('LOG_LEVEL', 'INFO', modes=[MODES.TEST])
    env.set('CACHE_ENABLED', 'true', modes=[MODES.TEST])

    print("\n   TEST Configuration:")
    print(f"   - DEBUG: {env.get('DEBUG')}")
    print(f"   - LOG_LEVEL: {env.get('LOG_LEVEL')}")
    print(f"   - CACHE_ENABLED: {env.get('CACHE_ENABLED')}")

    # Switch to PROD mode and set up production configuration
    env.mode = MODES.PROD
    env.set('DEBUG', 'false', modes=[MODES.PROD])
    env.set('LOG_LEVEL', 'WARNING', modes=[MODES.PROD])
    env.set('CACHE_ENABLED', 'true', modes=[MODES.PROD])

    print("\n   PROD Configuration:")
    print(f"   - DEBUG: {env.get('DEBUG')}")
    print(f"   - LOG_LEVEL: {env.get('LOG_LEVEL')}")
    print(f"   - CACHE_ENABLED: {env.get('CACHE_ENABLED')}")


if __name__ == '__main__':
    main()
