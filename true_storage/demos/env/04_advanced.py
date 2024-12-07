"""Advanced environment management features demo.

This demo shows advanced features like validation, filtering, and inheritance.
"""

from true_storage.env import Environment, MODES, EnvValidator

def main():
    """Run the advanced environment features demo."""
    print("\n=== Advanced Environment Features Demo ===\n")

    print("1. Environment Validation")
    print("----------------------")
    # Create environment with validation
    schema = {
        'PORT': int,
        'DEBUG': bool,
        'API_URL': str,
        'MAX_CONNECTIONS': int
    }
    env = Environment(validator=EnvValidator(schema))

    # Set valid values
    env.set({
        'PORT': '8080',           # Will be converted to int
        'DEBUG': 'true',          # Will be converted to bool
        'API_URL': 'http://api',  # Stays as string
        'MAX_CONNECTIONS': '100'  # Will be converted to int
    })

    print("Valid values set successfully:")
    print(f"  PORT: {env.get('PORT')} (type: {type(env.get('PORT'))})")
    print(f"  DEBUG: {env.get('DEBUG')} (type: {type(env.get('DEBUG'))})")
    print(f"  API_URL: {env.get('API_URL')} (type: {type(env.get('API_URL'))})")
    print(f"  MAX_CONNECTIONS: {env.get('MAX_CONNECTIONS')} (type: {type(env.get('MAX_CONNECTIONS'))})")

    # Try setting invalid values
    print("\nTrying to set invalid values:")
    try:
        env.set({'PORT': 'invalid_port'})  # Should fail validation
    except Exception as e:
        print(f"  PORT validation failed (expected): {e}")

    print("\n2. Environment Inheritance")
    print("-----------------------")
    # Create parent environment
    parent_env = Environment()
    parent_env.set({
        'PARENT_VAR': 'parent_value',
        'SHARED_VAR': 'parent_version'
    })

    # Create child environment
    child_env = Environment(parent=parent_env)
    child_env.set({'CHILD_VAR': 'child_value'})
    child_env.set({'SHARED_VAR': 'child_version'})  # Override parent

    print("Parent environment:")
    print(f"  PARENT_VAR: {parent_env.get('PARENT_VAR')}")
    print(f"  SHARED_VAR: {parent_env.get('SHARED_VAR')}")

    print("\nChild environment:")
    print(f"  PARENT_VAR: {child_env.get('PARENT_VAR')}") # Inherited
    print(f"  CHILD_VAR: {child_env.get('CHILD_VAR')}")   # Own variable
    print(f"  SHARED_VAR: {child_env.get('SHARED_VAR')}")  # Overridden

    print("\n3. Variable Filtering")
    print("------------------")
    # Set some variables for filtering
    env.set({
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'mydb',
        'API_KEY': 'secret',
        'API_VERSION': 'v1'
    })

    # Filter by prefix
    db_vars = env.filter('DB_')
    api_vars = env.filter('API_')

    print("Database-related variables:")
    for key, value in db_vars.items():
        print(f"  {key}: {value}")

    print("\nAPI-related variables:")
    for key, value in api_vars.items():
        print(f"  {key}: {value}")

    print("\n4. Mode-Specific Inheritance")
    print("-------------------------")
    # Set mode-specific variables in parent
    parent_env.set({'MODE_VAR': 'parent_mode_var'}, modes=[MODES.TEST])

    # Child inherits mode restrictions
    print("Mode-specific inheritance:")
    child_env.mode = MODES.TEST
    print(f"  MODE_VAR in TEST mode: {child_env.get('MODE_VAR')}")

    child_env.mode = MODES.DEV
    try:
        print(f"  MODE_VAR in DEV mode: {child_env.get('MODE_VAR')}")
    except Exception as e:
        print(f"  MODE_VAR access failed in DEV mode (expected): {e}")

if __name__ == "__main__":
    main()
