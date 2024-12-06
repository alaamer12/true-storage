"""Basic environment management demo.

This demo shows the basic functionality of the environment management system:
- Environment initialization
- Setting and getting variables
- Mode awareness
"""

from true_storage.env import Environment, MODES

def main():
    """Demonstrate basic environment functionality."""
    print("\n=== Basic Environment Demo ===\n")
    
    # Initialize environment
    env = Environment()
    print(f"1. Current Mode: {env.mode}")
    print(f"   Total Variables: {len(env.variables)}")
    
    # Basic variable operations
    print("\n2. Basic Variable Operations")
    print("   ------------------------")
    env.set('APP_NAME', 'TrueStorage')
    env.set('VERSION', '1.0.0')
    
    print(f"   APP_NAME: {env.get('APP_NAME')}")
    print(f"   VERSION: {env.get('VERSION')}")
    print(f"   UNDEFINED: {env.get('UNDEFINED', 'Not Set')}")
    
    # Dictionary-style access
    print("\n3. Dictionary-style Access")
    print("   ---------------------")
    env['DEBUG'] = 'true'
    print(f"   DEBUG: {env['DEBUG']}")
    
    # Environment info
    print("\n4. Environment Info")
    print("   ---------------")
    print(f"   {env}")

if __name__ == '__main__':
    main()
