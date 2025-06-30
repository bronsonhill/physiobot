#!/usr/bin/env python3
"""
Test script to verify that the ConfigManager loop issue is resolved.
This script simulates multiple ConfigManager instantiations that would occur
in a typical Streamlit application.
"""

import logging
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging to see the messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_config_manager_loop():
    """Test multiple ConfigManager instantiations to check for loops."""
    print("Testing ConfigManager instantiation loop...")
    print("=" * 50)
    
    # Import the modules that use ConfigManager
    from utils.config_manager import get_config_manager, ConfigManager
    from utils.mongodb_realtime import get_database_name
    
    print("\n1. Testing direct ConfigManager instantiation:")
    cm1 = ConfigManager()
    cm2 = ConfigManager()
    cm3 = ConfigManager()
    
    print("\n2. Testing get_config_manager() function:")
    cm4 = get_config_manager()
    cm5 = get_config_manager()
    
    print("\n3. Testing get_database_name() function:")
    db_name1 = get_database_name()
    db_name2 = get_database_name()
    db_name3 = get_database_name()
    
    print(f"\nDatabase name retrieved: {db_name1}")
    
    print("\n4. Testing configuration access:")
    config1 = cm1.config
    config2 = cm2.config
    config3 = cm3.config
    
    print(f"Config keys: {list(config1.keys())}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed successfully!")
    print("If you only see ONE 'Configuration loaded' message above, the loop issue is resolved.")
    print("If you see multiple messages, there's still a loop issue.")

if __name__ == "__main__":
    test_config_manager_loop() 