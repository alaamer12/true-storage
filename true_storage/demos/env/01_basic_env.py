"""Basic environment variable management demo.

This demo shows basic environment variable operations using the Environment class.
"""

from true_storage.env import Environment

def main():
    """Run the basic environment demo."""
    print("\n=== Basic Environment Demo ===\n")

    # Create environment instance
    env = Environment()

    # Set some basic variables
    env.set({
        'APP_NAME': 'DemoApp',
        'VERSION': '1.0.0',
        'DEBUG': 'true'
    })

    # Get variables
    print("1. Getting Variables")
    print("-------------------")
    print(f"APP_NAME: {env.get('APP_NAME')}")
    print(f"VERSION: {env.get('VERSION')}")
    print(f"DEBUG: {env.get('DEBUG')}")
    print(f"UNDEFINED: {env.get('UNDEFINED', 'default_value')}")  # With default value

    # Dictionary-style access
    print("\n2. Dictionary-style Access")
    print("-------------------------")
    env['PORT'] = '8080'  # Set using dict style
    print(f"PORT: {env['PORT']}")  # Get using dict style
    del env['PORT']  # Delete using dict style
    print(f"PORT (deleted): {env.get('PORT', 'not found')}")

    # Environment information
    print("\n3. Environment Information")
    print("-------------------------")
    print(f"Number of variables: {len(env)}")
    print(f"All variables: {env.variables}")

if __name__ == "__main__":
    main()
