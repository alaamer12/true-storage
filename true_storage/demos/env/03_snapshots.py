"""Environment snapshots and state management demo.

This demo shows snapshot functionality:
- Creating environment snapshots
- Rolling back to previous states
- Managing multiple configurations
"""

from true_storage.env import Environment, MODES


def main():
    """Demonstrate environment snapshot functionality."""
    print("\n=== Environment Snapshots Demo ===\n")

    env = Environment()

    # 1. Initial setup
    print("1. Initial Setup")
    print("   -------------")
    env.set('DB_URL', 'localhost:5432', modes=[MODES.DEV, MODES.TEST])
    env.set('API_KEY', 'test-key-123', modes=[MODES.TEST])
    print(f"   Initial DB_URL: {env.get('DB_URL')}")

    # 2. Create snapshot
    print("\n2. Creating Snapshot")
    print("   ----------------")
    snapshot = env.create_snapshot()
    print(f"   Snapshot created at: {snapshot.timestamp}")

    # 3. Make changes
    print("\n3. Making Changes")
    print("   --------------")
    env.set('DB_URL', 'new-db:5432', modes=[MODES.DEV, MODES.TEST])
    print(f"   New DB_URL: {env.get('DB_URL')}")

    # 4. Rollback
    print("\n4. Rolling Back")
    print("   ------------")
    env.rollback(snapshot)
    print(f"   After rollback - DB_URL: {env.get('DB_URL')}")

    # 5. Multiple configurations
    print("\n5. Multiple Configurations")
    print("   -----------------------")

    # Development config
    with env.with_mode(MODES.DEV):
        env.set('LOG_LEVEL', 'DEBUG')
        env.set('CACHE_SIZE', '1024')
        dev_snapshot = env.create_snapshot()

    # Production config
    with env.with_mode(MODES.PROD):
        env.set('LOG_LEVEL', 'WARNING')
        env.set('CACHE_SIZE', '4096')
        prod_snapshot = env.create_snapshot()

    # Switch between configurations
    print("\n   Development Config:")
    env.rollback(dev_snapshot)
    print(f"   LOG_LEVEL: {env.get('LOG_LEVEL')}")
    print(f"   CACHE_SIZE: {env.get('CACHE_SIZE')}")

    print("\n   Production Config:")
    env.rollback(prod_snapshot)
    print(f"   LOG_LEVEL: {env.get('LOG_LEVEL')}")
    print(f"   CACHE_SIZE: {env.get('CACHE_SIZE')}")


if __name__ == '__main__':
    main()
