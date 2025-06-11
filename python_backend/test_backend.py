#!/usr/bin/env python3
"""
GraphiVault Backend Test Suite
Comprehensive tests for the GraphiVault backend architecture
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
import unittest
from datetime import datetime, timezone

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    import core_engine
    import crypto_controller
    import vault_manager
    import image_processor
    import tag_manager
    import search_engine
    import audit_logger
    import session_manager
    import storage_interface
    import ipc_gateway
    
    from core_engine import GraphiVaultCore
    from crypto_controller import CryptoController
    from vault_manager import VaultManager
    from image_processor import ImageProcessor
    from tag_manager import TagManager
    from search_engine import SearchEngine
    from audit_logger import AuditLogger
    from session_manager import SessionManager
    from storage_interface import StorageInterface
    from ipc_gateway import IPCGateway
except ImportError as e:
    print(f"Failed to import backend modules: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


class TestGraphiVaultBackend(unittest.TestCase):
    """Test suite for GraphiVault backend"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.vault_path = self.test_dir / "test_vault"
        self.master_password = "test_password_123"
        
        print(f"Test vault created at: {self.vault_path}")
    
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        print("Test vault cleaned up")
    
    def test_crypto_controller(self):
        """Test crypto controller functionality"""
        print("\n=== Testing Crypto Controller ===")
        
        crypto = CryptoController({})
        
        # Test key initialization
        self.assertTrue(crypto.initialize_master_key(self.master_password))
        self.assertTrue(crypto.is_initialized())
        
        # Test data encryption/decryption
        test_data = b"Hello, GraphiVault!"
        encrypted_data = crypto.encrypt_data(test_data)
        decrypted_data = crypto.decrypt_data(encrypted_data)
        
        self.assertEqual(test_data, decrypted_data)
        print("✓ Data encryption/decryption working")
        
        # Test tag keychain encryption
        tag_data = b"secret_tag_data"
        encrypted_tags = crypto.encrypt_with_tag_keychain(tag_data)
        decrypted_tags = crypto.decrypt_with_tag_keychain(encrypted_tags)
        
        self.assertEqual(tag_data, decrypted_tags)
        print("✓ Tag keychain encryption working")
        
        # Test key clearing
        crypto.clear_keys()
        self.assertFalse(crypto.is_initialized())
        print("✓ Key clearing working")
    
    def test_vault_manager(self):
        """Test vault manager functionality"""
        print("\n=== Testing Vault Manager ===")
        
        crypto = CryptoController({})
        crypto.initialize_master_key(self.master_password)
        
        vault_manager = VaultManager(self.vault_path, crypto)
        
        # Test vault creation
        self.assertTrue(vault_manager.create_vault())
        self.assertTrue(vault_manager.vault_exists())
        print("✓ Vault creation working")
        
        # Test vault configuration
        config = vault_manager.get_vault_config()
        self.assertIsNotNone(config)
        self.assertIn('vault_id', config)
        print("✓ Vault configuration working")
        
        # Test vault statistics
        stats = vault_manager.get_vault_stats()
        self.assertIn('total_images', stats)
        print("✓ Vault statistics working")
        
        # Test vault integrity
        integrity = vault_manager.validate_vault_integrity()
        self.assertTrue(integrity['valid'])
        print("✓ Vault integrity validation working")
    
    def test_tag_manager(self):
        """Test tag manager functionality"""
        print("\n=== Testing Tag Manager ===")
        
        crypto = CryptoController({})
        crypto.initialize_master_key(self.master_password)
        
        tag_manager = TagManager(crypto)
        
        # Test tag encryption/decryption
        test_tags = ["vacation", "beach", "summer_2024"]
        encrypted_tags = tag_manager.encrypt_tags(test_tags)
        decrypted_tags = tag_manager.decrypt_tags(encrypted_tags)
        
        self.assertEqual(sorted(test_tags), sorted(decrypted_tags))
        print("✓ Tag encryption/decryption working")
        
        # Test tag suggestions
        suggestions = tag_manager.suggest_tags("vac", limit=5)
        self.assertIsInstance(suggestions, list)
        print("✓ Tag suggestions working")
        
        # Test tag statistics
        stats = tag_manager.get_tag_statistics()
        self.assertIn('total_unique_tags', stats)
        print("✓ Tag statistics working")
    
    def test_search_engine(self):
        """Test search engine functionality"""
        print("\n=== Testing Search Engine ===")
        
        search_engine = SearchEngine()
        
        # Create test data
        test_records = [
            {
                'name': 'vacation_beach.jpg',
                'tags': ['vacation', 'beach', 'summer'],
                'metadata': {'location': 'Hawaii', 'camera': 'Canon EOS'},
                'size': 2048000,
                'mimeType': 'image/jpeg',
                'dateAdded': '2024-01-15T10:30:00Z'
            },
            {
                'name': 'sunset_mountain.png',
                'tags': ['sunset', 'mountain', 'landscape'],
                'metadata': {'location': 'Colorado', 'camera': 'Nikon D750'},
                'size': 5120000,
                'mimeType': 'image/png',
                'dateAdded': '2024-02-20T18:45:00Z'
            }
        ]
        
        # Test search matching
        self.assertTrue(search_engine.matches_query(
            "vacation", test_records[0]['name'], 
            test_records[0]['tags'], test_records[0]['metadata']
        ))
        print("✓ Search matching working")
        
        # Test search and ranking
        results = search_engine.search_and_rank("beach", test_records)
        self.assertTrue(len(results) > 0)
        print("✓ Search and ranking working")
        
        # Test search statistics
        stats = search_engine.get_search_statistics(test_records)
        self.assertEqual(stats['total_images'], 2)
        print("✓ Search statistics working")
    
    def test_session_manager(self):
        """Test session manager functionality"""
        print("\n=== Testing Session Manager ===")
        
        session_manager = SessionManager({})
        
        # Test session creation
        session_id = session_manager.create_session(self.master_password)
        self.assertIsNotNone(session_id)
        print("✓ Session creation working")
        
        # Test session validation
        self.assertTrue(session_manager.validate_session(session_id))
        print("✓ Session validation working")
        
        # Test session info
        info = session_manager.get_session_info()
        self.assertTrue(info['active'])
        print("✓ Session info working")
        
        # Test session destruction
        self.assertTrue(session_manager.destroy_session())
        self.assertFalse(session_manager.is_session_active())
        print("✓ Session destruction working")
    
    def test_audit_logger(self):
        """Test audit logger functionality"""
        print("\n=== Testing Audit Logger ===")
        
        log_file = self.test_dir / "test_audit.log"
        audit_logger = AuditLogger(str(log_file))
        
        # Test event logging
        event_data = {'test': 'data', 'timestamp': datetime.now(timezone.utc).isoformat()}
        self.assertTrue(audit_logger.log_event('test_event', event_data))
        print("✓ Event logging working")
        
        # Test event retrieval
        events = audit_logger.get_security_events(24)
        self.assertIsInstance(events, list)
        print("✓ Event retrieval working")
        
        # Test audit summary
        summary = audit_logger.get_audit_summary(24)
        self.assertIn('total_events', summary)
        print("✓ Audit summary working")
        
        # Test log integrity
        integrity = audit_logger.verify_log_integrity()
        self.assertTrue(integrity['valid'])
        print("✓ Log integrity verification working")
    
    def test_storage_interface(self):
        """Test storage interface functionality"""
        print("\n=== Testing Storage Interface ===")
        
        crypto = CryptoController({})
        crypto.initialize_master_key(self.master_password)
        
        db_path = self.test_dir / "test.db"
        storage = StorageInterface(str(db_path), crypto)
        
        # Test vault settings
        self.assertTrue(storage.set_vault_setting('test_key', 'test_value'))
        value = storage.get_vault_setting('test_key')
        self.assertEqual(value, 'test_value')
        print("✓ Vault settings working")
        
        # Test encrypted settings
        self.assertTrue(storage.set_vault_setting('secret_key', 'secret_value', encrypted=True))
        secret_value = storage.get_vault_setting('secret_key')
        self.assertEqual(secret_value, 'secret_value')
        print("✓ Encrypted settings working")
        
        # Test audit logging
        event_data = {'action': 'test', 'result': 'success'}
        self.assertTrue(storage.log_audit_event('test_event', event_data))
        print("✓ Storage audit logging working")
        
        # Test storage statistics
        stats = storage.get_storage_stats()
        self.assertIn('total_images', stats)
        print("✓ Storage statistics working")
        
        storage.close()
    
    def test_core_engine_integration(self):
        """Test core engine integration"""
        print("\n=== Testing Core Engine Integration ===")
        
        core = GraphiVaultCore(str(self.vault_path))
        
        # Test vault initialization
        self.assertTrue(core.initialize_vault(self.master_password))
        print("✓ Core engine vault initialization working")
        
        # Test vault locking/unlocking
        self.assertTrue(core.lock_vault())
        self.assertTrue(core.unlock_vault(self.master_password))
        print("✓ Core engine vault lock/unlock working")
        
        # Note: Image operations would require actual image files for full testing
        print("✓ Core engine integration basic tests passed")
    
    def test_ipc_gateway(self):
        """Test IPC gateway functionality"""
        print("\n=== Testing IPC Gateway ===")
        
        gateway = IPCGateway(str(self.vault_path))
        
        # Test vault initialization
        result = gateway.initialize_vault(self.master_password)
        self.assertTrue(result['success'])
        print("✓ IPC gateway vault initialization working")
        
        # Test vault stats
        stats_result = gateway.get_vault_stats()
        self.assertTrue(stats_result['success'])
        self.assertIn('statistics', stats_result)
        print("✓ IPC gateway vault stats working")
        
        # Test vault locking
        lock_result = gateway.lock_vault()
        self.assertTrue(lock_result['success'])
        print("✓ IPC gateway vault locking working")


def run_performance_tests():
    """Run basic performance tests"""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    import time
    
    # Test crypto performance
    print("\n--- Crypto Performance ---")
    crypto = CryptoController({})
    crypto.initialize_master_key("performance_test_password")
    
    # Test data encryption speed
    test_data = b"X" * (1024 * 1024)  # 1MB of data
    
    start_time = time.time()
    encrypted = crypto.encrypt_data(test_data)
    encrypt_time = time.time() - start_time
    
    start_time = time.time()
    decrypted = crypto.decrypt_data(encrypted)
    decrypt_time = time.time() - start_time
    
    print(f"✓ 1MB encryption: {encrypt_time:.3f}s ({1/encrypt_time:.1f} MB/s)")
    print(f"✓ 1MB decryption: {decrypt_time:.3f}s ({1/decrypt_time:.1f} MB/s)")
    
    crypto.clear_keys()


def main():
    """Run all tests"""
    print("GraphiVault Backend Test Suite")
    print("="*50)
      # Check dependencies
    try:
        import PIL
        from PIL import Image
        print("✓ PIL/Pillow available")
    except ImportError:
        print("✗ PIL/Pillow not available - some tests may fail")
    
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher
        print("✓ Cryptography library available")
    except ImportError:
        print("✗ Cryptography library not available - tests will fail")
        return 1
    
    # Run unit tests
    print("\n" + "="*50)
    print("UNIT TESTS")
    print("="*50)
    
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    print("\n" + "="*50)
    print("TEST SUITE COMPLETED")
    print("="*50)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
