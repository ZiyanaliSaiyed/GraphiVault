#!/usr/bin/env python3
"""
Simple test script to verify GraphiVault backend imports and basic functionality
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing GraphiVault Backend Imports...")
    
    try:
        import crypto_controller
        print("✓ crypto_controller imported")
    except Exception as e:
        print(f"✗ crypto_controller failed: {e}")
        return False
    
    try:
        import vault_manager
        print("✓ vault_manager imported")
    except Exception as e:
        print(f"✗ vault_manager failed: {e}")
        return False
    
    try:
        import image_processor
        print("✓ image_processor imported")
    except Exception as e:
        print(f"✗ image_processor failed: {e}")
        return False
    
    try:
        import tag_manager
        print("✓ tag_manager imported")
    except Exception as e:
        print(f"✗ tag_manager failed: {e}")
        return False
    
    try:
        import search_engine
        print("✓ search_engine imported")
    except Exception as e:
        print(f"✗ search_engine failed: {e}")
        return False
    
    try:
        import audit_logger
        print("✓ audit_logger imported")
    except Exception as e:
        print(f"✗ audit_logger failed: {e}")
        return False
    
    try:
        import session_manager
        print("✓ session_manager imported")
    except Exception as e:
        print(f"✗ session_manager failed: {e}")
        return False
    
    try:
        import storage_interface
        print("✓ storage_interface imported")
    except Exception as e:
        print(f"✗ storage_interface failed: {e}")
        return False
    
    try:
        import core_engine
        print("✓ core_engine imported")
    except Exception as e:
        print(f"✗ core_engine failed: {e}")
        return False
    
    try:
        import ipc_gateway
        print("✓ ipc_gateway imported")
    except Exception as e:
        print(f"✗ ipc_gateway failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting Basic Functionality...")
    
    try:
        from crypto_controller import CryptoController
        
        # Test crypto controller
        crypto = CryptoController({})
        success = crypto.initialize_master_key("test_password")
        if success:
            print("✓ CryptoController initialization works")
            
            # Test encryption/decryption
            test_data = b"Hello GraphiVault!"
            encrypted = crypto.encrypt_data(test_data)
            decrypted = crypto.decrypt_data(encrypted)
            
            if test_data == decrypted:
                print("✓ Data encryption/decryption works")
            else:
                print("✗ Data encryption/decryption failed")
                return False
            
            crypto.clear_keys()
        else:
            print("✗ CryptoController initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False
    
    return True

def test_ipc_gateway():
    """Test IPC Gateway"""
    print("\nTesting IPC Gateway...")
    
    try:
        from ipc_gateway import IPCGateway
        import tempfile
        import shutil
        
        # Create temporary vault
        temp_dir = Path(tempfile.mkdtemp())
        vault_path = temp_dir / "test_vault"
        
        try:
            gateway = IPCGateway(str(vault_path))
            
            # Test vault initialization
            result = gateway.initialize_vault("test_password_123")
            if result.get('success', False):
                print("✓ IPC Gateway vault initialization works")
                
                # Test vault stats
                stats_result = gateway.get_vault_stats()
                if stats_result.get('success', False):
                    print("✓ IPC Gateway vault stats works")
                else:
                    print(f"✗ IPC Gateway vault stats failed: {stats_result.get('error', 'Unknown error')}")
                    return False
                  # Test vault locking
                lock_result = gateway.lock_vault()
                if lock_result.get('success', False):
                    print("✓ IPC Gateway vault locking works")
                else:
                    print(f"✗ IPC Gateway vault locking failed: {lock_result.get('error', 'Unknown error')}")
                    return False
                    
            else:
                print(f"✗ IPC Gateway vault initialization failed: {result.get('error', 'Unknown error')}")
                return False
                
        finally:
            # Cleanup - close any database connections first
            try:
                if hasattr(gateway, 'core') and gateway.core and hasattr(gateway.core, 'storage'):
                    if gateway.core.storage:
                        gateway.core.storage.close()
                # Small delay to ensure Windows releases file handles
                import time
                time.sleep(0.1)
            except:
                pass
            
            # Cleanup
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except PermissionError:
                print("Note: Temporary files may need manual cleanup due to Windows file locks")
                pass
                
    except Exception as e:
        print(f"✗ IPC Gateway test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("GraphiVault Backend - Quick Verification")
    print("=" * 60)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required modules
    print("\nChecking dependencies...")
    try:
        import cryptography
        print("✓ cryptography available")
    except ImportError:
        print("✗ cryptography not available")
        print("Install with: pip install cryptography")
        return 1
    
    try:
        import sqlite3
        print("✓ sqlite3 available")
    except ImportError:
        print("✗ sqlite3 not available")
        return 1
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return 1
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed!")
        return 1
    
    # Test IPC Gateway
    if not test_ipc_gateway():
        print("\n❌ IPC Gateway tests failed!")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("GraphiVault Backend is ready for integration!")
    print("=" * 60)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
