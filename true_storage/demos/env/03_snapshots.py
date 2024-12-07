"""Environment snapshot and rollback demo.

This demo shows how to use environment snapshots for backup and rollback.
"""

from true_storage.env import Environment, MODES

def main():
    """Run the environment snapshot demo."""
    print("\n=== Environment Snapshot Demo ===\n")

    # Create environment instance
    env = Environment()

    print("1. Initial Setup")
    print("--------------")
    # Set initial variables
    env.set({
        'APP_NAME': 'TrueStorage',
        'VERSION': '1.0.0',
        'DEBUG': 'false'
    })

    # Display initial state
    print("Initial variables:")
    print(f"  APP_NAME: {env.get('APP_NAME')}")
    print(f"  VERSION: {env.get('VERSION')}")
    print(f"  DEBUG: {env.get('DEBUG')}")

    print("\n2. Creating Snapshot")
    print("------------------")
    # Create a snapshot
    snapshot = env.create_snapshot()
    print(f"Snapshot created at: {snapshot.timestamp}")
    print(f"Variables in snapshot: {len(snapshot.variables)}")

    print("\n3. Making Changes")
    print("---------------")
    # Make some changes
    env.set({
        'APP_NAME': 'TrueStorage-Dev',
        'DEBUG': 'true',
        'NEW_VAR': 'new-value'
    })

    print("Variables after changes:")
    print(f"  APP_NAME: {env.get('APP_NAME')}")
    print(f"  DEBUG: {env.get('DEBUG')}")
    print(f"  NEW_VAR: {env.get('NEW_VAR')}")

    print("\n4. Rolling Back")
    print("-------------")
    # Roll back to snapshot
    env.rollback(snapshot)

    print("Variables after rollback:")
    print(f"  APP_NAME: {env.get('APP_NAME')}")
    print(f"  VERSION: {env.get('VERSION')}")
    print(f"  DEBUG: {env.get('DEBUG')}")
    print(f"  NEW_VAR: {env.get('NEW_VAR', 'Not Found')}")

    print("\n5. Mode-Specific Snapshots")
    print("-----------------------")
    # Set mode-specific variables
    env.set({'TEST_VAR': 'test-value'}, modes=[MODES.TEST])
    env.set({'PROD_VAR': 'prod-value'}, modes=[MODES.PROD])

    # Create new snapshot
    mode_snapshot = env.create_snapshot()

    # Make mode-specific changes
    env.set({'TEST_VAR': 'modified-test'}, modes=[MODES.TEST])
    env.set({'PROD_VAR': 'modified-prod'}, modes=[MODES.PROD])

    print("Variables before mode-specific rollback:")
    env.mode = MODES.TEST
    print(f"  TEST_VAR (TEST mode): {env.get('TEST_VAR', 'Not Found')}")
    env.mode = MODES.PROD
    print(f"  PROD_VAR (PROD mode): {env.get('PROD_VAR', 'Not Found')}")

    # Roll back mode-specific changes
    env.rollback(mode_snapshot)

    print("\nVariables after mode-specific rollback:")
    env.mode = MODES.TEST
    print(f"  TEST_VAR (TEST mode): {env.get('TEST_VAR', 'Not Found')}")
    env.mode = MODES.PROD
    print(f"  PROD_VAR (PROD mode): {env.get('PROD_VAR', 'Not Found')}")

if __name__ == "__main__":
    main()
