#!/usr/bin/env python3
"""
GraphiVault Database Integration Test
Test the database initialization and basic operations
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from database_init import DatabaseInitializer
    from storage_interface import StorageInterface, ImageRecord
    from crypto_controller import CryptoController
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)


def test_database_initialization():
    """Test basic database initialization"""
    print("\n=== Testing Database Initialization ===")
    
    # Create temporary test directory
    test_dir = Path(tempfile.mkdtemp())
    vault_path = test_dir / "test_vault"
    
    try:
        # Test vault creation
        initializer = DatabaseInitializer(str(vault_path))
        success = initializer.initialize_vault("test_password_123")
        
        if success:
            print("✓ Vault initialization successful")
            
            # Check vault structure
            required_dirs = ['data', 'encrypted', 'thumbnails', 'temp', 'backups']
            for dir_name in required_dirs:
                dir_path = vault_path / dir_name
                if dir_path.exists():
                    print(f"✓ Directory '{dir_name}' created")
                else:
                    print(f"✗ Directory '{dir_name}' missing")
            
            # Check database file
            db_path = vault_path / "data" / "graphivault.db"
            if db_path.exists():
                print("✓ Database file created")
                print(f"  Database size: {db_path.stat().st_size} bytes")
            else:
                print("✗ Database file missing")
            
            # Test vault info retrieval
            vault_info = initializer.get_vault_info()
            if vault_info:
                print("✓ Vault info retrieved")
                print(f"  Vault ID: {vault_info.get('vault_id', 'N/A')}")
                print(f"  Created: {vault_info.get('created_at', 'N/A')}")
                print(f"  Version: {vault_info.get('version', 'N/A')}")
            else:
                print("✗ Failed to retrieve vault info")
        else:
            print("✗ Vault initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Exception during vault initialization: {e}")
        return False
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print("✓ Test cleanup completed")
    
    return True


def test_database_operations():
    """Test basic database CRUD operations"""
    print("\n=== Testing Database Operations ===")
    
    # Create temporary test directory
    test_dir = Path(tempfile.mkdtemp())
    vault_path = test_dir / "test_vault"
    
    try:
        # Initialize vault
        initializer = DatabaseInitializer(str(vault_path))
        if not initializer.initialize_vault("test_password_123"):
            print("✗ Failed to initialize vault for operations test")
            return False
        
        # Initialize crypto controller
        crypto = CryptoController({})
        if not crypto.initialize_master_key("test_password_123"):
            print("✗ Failed to initialize crypto controller")
            return False
        
        # Initialize storage interface
        db_path = vault_path / "data" / "graphivault.db"
        storage = StorageInterface(str(db_path), crypto)
        
        # Test vault metadata operations
        test_key = "test_setting"
        test_value = "test_value_123"
        
        if storage.set_vault_meta(test_key, test_value):
            print("✓ Vault metadata write successful")
        else:
            print("✗ Vault metadata write failed")
            return False
        
        retrieved_value = storage.get_vault_meta(test_key)
        if retrieved_value == test_value:
            print("✓ Vault metadata read successful")
        else:
            print(f"✗ Vault metadata read failed: expected '{test_value}', got '{retrieved_value}'")
            return False
        
        # Test auth logging
        if storage.log_auth_event("test_event", "success", "Database test event"):
            print("✓ Auth event logging successful")
        else:
            print("✗ Auth event logging failed")
            return False
        
        # Test image record creation (mock)
        from datetime import datetime, timezone
        test_image = ImageRecord(
            id=0,  # Will be auto-generated
            file_hash="test_hash_123456789abcdef",
            file_name="test_encrypted_filename",
            storage_path="encrypted/test_image.enc",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            file_size=1024000,
            is_deleted=False
        )
        
        if storage.store_image(test_image):
            print("✓ Image record storage successful")
        else:
            print("✗ Image record storage failed")
            return False
        
        # Clean up
        storage.close()
        crypto.clear_keys()
        
    except Exception as e:
        print(f"✗ Exception during database operations test: {e}")
        return False
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print("✓ Operations test cleanup completed")
    
    return True


def main():
    """Run all database integration tests"""
    print("GraphiVault Database Integration Tests")
    print("=" * 50)
    
    # Check if we're in the right directory
    backend_dir = Path(__file__).parent
    if not (backend_dir / "database_init.py").exists():
        print("✗ Please run this script from the python_backend directory")
        return 1
    
    all_passed = True
    
    # Run tests
    if not test_database_initialization():
        all_passed = False
    
    if not test_database_operations():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All database integration tests passed!")
        return 0
    else:
        print("✗ Some database integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
