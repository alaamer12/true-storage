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
    MODES.add_custom_stage('STAGING', 'staging')
    env.set('STAGE_URL', 'staging.example.com', modes=[MODES.STAGING])
    print(f"   Available Modes: {[mode.name for mode in MODES]}")
    print(f"   STAGE_URL: {env.get('STAGE_URL')}")
    
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
    
    # 4. Complex mode handling
    print("\n4. Complex Mode Handling")
    print("   -------------------")
    
    # Define environment configurations
    configs = {
        MODES.DEV: {
            'DEBUG': 'true',
            'LOG_LEVEL': 'DEBUG',
            'CACHE_ENABLED': 'false'
        },
        MODES.TEST: {
            'DEBUG': 'true',
            'LOG_LEVEL': 'INFO',
            'CACHE_ENABLED': 'true'
        },
        MODES.PROD: {
            'DEBUG': 'false',
            'LOG_LEVEL': 'WARNING',
            'CACHE_ENABLED': 'true'
        }
    }
    
    # Apply configurations
    for mode, config in configs.items():
        with env.with_mode(mode):
            for key, value in config.items():
                env.set(key, value, modes=[mode])
    
    # Display configurations
    for mode in [MODES.DEV, MODES.TEST, MODES.PROD]:
        print(f"\n   {mode.name} Configuration:")
        with env.with_mode(mode):
            print(f"   - DEBUG: {env.get('DEBUG')}")
            print(f"   - LOG_LEVEL: {env.get('LOG_LEVEL')}")
            print(f"   - CACHE_ENABLED: {env.get('CACHE_ENABLED')}")

if __name__ == '__main__':
    main()
