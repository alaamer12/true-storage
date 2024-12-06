"""Mode-specific environment management demo.

This demo shows mode-specific functionality:
- Setting mode-specific variables
- Mode-based access control
- Mode switching
- Mode-specific decorators
"""

from true_storage.env import Environment, MODES


def main():
    """Demonstrate mode-specific environment functionality."""
    print("\n=== Mode-Specific Environment Demo ===\n")

    env = Environment()

    # 1. Setting mode-specific variables
    print("1. Mode-Specific Variables")
    print("   ----------------------")
    env.set('DB_URL', 'localhost:5432', modes=[MODES.DEV, MODES.TEST])
    env.set('API_KEY', 'test-key-123', modes=[MODES.TEST])
    env.set('PROD_SECRET', 'secret-123', modes=[MODES.PROD])
    env.set('APP_NAME', 'TrueStorage', modes=[MODES.ALL])

    print(f"   Mode Mappings: {env.mode_mappings}")

    # 2. Mode-based access
    print("\n2. Mode-Based Access")
    print("   ----------------")

    # DEV mode access
    print("\n   In DEV mode:")
    with env.with_mode(MODES.DEV):
        print(f"   APP_NAME: {env.get('APP_NAME')}")  # Accessible (ALL mode)
        print(f"   DB_URL: {env.get('DB_URL')}")  # Accessible (DEV mode)
        try:
            print(f"   API_KEY: {env.get('API_KEY')}")  # Not accessible
        except Exception as e:
            print(f"   API_KEY: {e}")

    # TEST mode access
    print("\n   In TEST mode:")
    with env.with_mode(MODES.TEST):
        print(f"   APP_NAME: {env.get('APP_NAME')}")  # Accessible (ALL mode)
        print(f"   DB_URL: {env.get('DB_URL')}")  # Accessible (TEST mode)
        print(f"   API_KEY: {env.get('API_KEY')}")  # Accessible (TEST mode)

    # 3. Mode-specific decorator
    print("\n3. Mode-Specific Decorator")
    print("   ----------------------")

    @env.mark(MODES.TEST)
    def get_test_config():
        return env.get('API_KEY')

    @env.mark(MODES.PROD)
    def get_prod_secret():
        return env.get('PROD_SECRET')

    # Execute in TEST mode
    try:
        print(f"   Test Config: {get_test_config()}")
    except Exception as e:
        print(f"   Test Config Error: {e}")

    # Execute in PROD mode
    try:
        print(f"   Prod Secret: {get_prod_secret()}")
    except Exception as e:
        print(f"   Prod Secret Error: {e}")


if __name__ == '__main__':
    main()
