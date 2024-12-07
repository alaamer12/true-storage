"""Mode-specific environment variable management demo.

This demo shows how to use mode-specific environment variables and the mode decorator.
"""

from true_storage.env import Environment, MODES

def main():
    """Run the mode-specific environment demo."""
    print("\n=== Mode-Specific Environment Demo ===\n")

    # Create environment instance
    env = Environment()

    print("1. Setting Mode-Specific Variables")
    print("--------------------------------")
    # Set variables with different mode access
    env.set({'APP_NAME': 'TrueStorage'}, modes=[MODES.ALL])  # Available in all modes
    env.set({'DB_URL': 'localhost:5432'}, modes=[MODES.DEV, MODES.TEST])  # Dev and test
    env.set({'API_KEY': 'test-key-123'}, modes=[MODES.TEST])  # Only in test
    env.set({'PROD_SECRET': 'secret-123'}, modes=[MODES.PROD])  # Only in production

    # Define mode-specific functions
    @env.mark(MODES.TEST)
    def get_test_config():
        """Get test configuration."""
        return {
            'db_url': env.get('DB_URL'),
            'api_key': env.get('API_KEY')
        }

    @env.mark(MODES.PROD)
    def get_prod_config():
        """Get production configuration."""
        return {
            'app_name': env.get('APP_NAME'),
            'secret': env.get('PROD_SECRET')
        }

    print("\n2. Accessing Variables in Different Modes")
    print("---------------------------------------")

    # Test DEV mode
    env.mode = MODES.DEV
    print(f"DEV Mode:")
    print(f"  APP_NAME: {env.get('APP_NAME')}")  # Should work
    print(f"  DB_URL: {env.get('DB_URL')}")      # Should work
    try:
        print(f"  API_KEY: {env.get('API_KEY')}")  # Should fail
    except Exception as e:
        print(f"  API_KEY access failed (expected): {e}")

    # Test TEST mode
    env.mode = MODES.TEST
    print(f"\nTEST Mode:")
    print(f"  APP_NAME: {env.get('APP_NAME')}")  # Should work
    print(f"  DB_URL: {env.get('DB_URL')}")      # Should work
    print(f"  API_KEY: {env.get('API_KEY')}")    # Should work
    try:
        print(f"  PROD_SECRET: {env.get('PROD_SECRET')}")  # Should fail
    except Exception as e:
        print(f"  PROD_SECRET access failed (expected): {e}")

    print("\n3. Using Mode-Specific Functions")
    print("------------------------------")
    try:
        # Try to get test config in TEST mode
        env.mode = MODES.TEST
        test_config = get_test_config()
        print(f"Test Config (TEST mode): {test_config}")

        # Try to get prod config in TEST mode (should fail)
        prod_config = get_prod_config()
        print(f"Prod Config (TEST mode): {prod_config}")
    except Exception as e:
        print(f"Prod config in TEST mode failed (expected): {e}")

    try:
        # Try to get prod config in PROD mode
        env.mode = MODES.PROD
        prod_config = get_prod_config()
        print(f"\nProd Config (PROD mode): {prod_config}")

        # Try to get test config in PROD mode (should fail)
        test_config = get_test_config()
        print(f"Test Config (PROD mode): {test_config}")
    except Exception as e:
        print(f"Test config in PROD mode failed (expected): {e}")

if __name__ == "__main__":
    main()
