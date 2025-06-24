#!/usr/bin/env python3
"""
GraphiVault Backend Test Script
Standalone test suite for the GraphiVault backend
"""

import os
import sys
import time
import json
import argparse
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import diagnostic logger
from diagnostics.utils.logger import DiagnosticLogger

# Import vault validator
from diagnostics.vault_validator import VaultValidator

class BackendTester:
    """
    Tests the GraphiVault backend components independently
    
    Performs tests on:
    - CryptoController
    - VaultManager
    - Session management
    - Database operations
    - API functionality
    """
    
    def __init__(self, vault_path: Path, log: DiagnosticLogger):
        """Initialize tester with vault path"""
        self.vault_path = vault_path
        self.log = log
        self.issues = []
        
        # Components to test
        self.crypto = None
        self.vault_manager = None
        self.core_engine = None
        self.ipc_gateway = None
        
        # Test results
        self.crypto_success = False
        self.vault_manager_success = False
        self.core_success = False
        self.ipc_success = False
        
    def import_backend_modules(self) -> bool:
        """Import required backend modules"""
        self.log.step("Importing Backend Modules")
        
        modules = {
            'crypto_controller': None,
            'vault_manager': None,
            'core_engine': None,
            'storage_interface': None,
            'session_manager': None,
            'ipc_gateway': None
        }
        
        import_success = True
        
        # Try to import each module
        try:
            from crypto.crypto_controller import CryptoController
            modules['crypto_controller'] = CryptoController
            self.log.success("Imported CryptoController")
        except Exception as e:
            self.log.failure(f"Failed to import CryptoController: {e}")
            self.issues.append(f"Failed to import CryptoController: {str(e)}")
            import_success = False
        
        try:
            from core.vault_manager import VaultManager
            modules['vault_manager'] = VaultManager
            self.log.success("Imported VaultManager")
        except Exception as e:
            self.log.failure(f"Failed to import VaultManager: {e}")
            self.issues.append(f"Failed to import VaultManager: {str(e)}")
            import_success = False
        
        try:
            from core.core_engine import GraphiVaultCore
            modules['core_engine'] = GraphiVaultCore
            self.log.success("Imported GraphiVaultCore")
        except Exception as e:
            self.log.failure(f"Failed to import GraphiVaultCore: {e}")
            self.issues.append(f"Failed to import GraphiVaultCore: {str(e)}")
            import_success = False
        
        try:
            from storage.storage_interface import StorageInterface
            modules['storage_interface'] = StorageInterface
            self.log.success("Imported StorageInterface")
        except Exception as e:
            self.log.failure(f"Failed to import StorageInterface: {e}")
            self.issues.append(f"Failed to import StorageInterface: {str(e)}")
            import_success = False
        
        try:
            from core.session_manager import SessionManager
            modules['session_manager'] = SessionManager
            self.log.success("Imported SessionManager")
        except Exception as e:
            self.log.failure(f"Failed to import SessionManager: {e}")
            self.issues.append(f"Failed to import SessionManager: {str(e)}")
            import_success = False
        
        try:
            from ipc.ipc_gateway import IPCGateway
            modules['ipc_gateway'] = IPCGateway
            self.log.success("Imported IPCGateway")
        except Exception as e:
            self.log.failure(f"Failed to import IPCGateway: {e}")
            self.issues.append(f"Failed to import IPCGateway: {str(e)}")
            import_success = False
        
        self.modules = {k: v for k, v in modules.items() if v is not None}
        
        self.log.result("Module Imports", import_success)
        return import_success
    
    def test_crypto_controller(self, test_password: str = "test123") -> bool:
        """Test CryptoController functionality"""
        self.log.step("Testing CryptoController")
        
        if 'crypto_controller' not in self.modules:
            self.log.error("CryptoController module not available")
            return False
        
        CryptoController = self.modules['crypto_controller']
        
        try:
            # Create crypto controller
            self.log.info("Creating CryptoController instance")
            crypto = CryptoController({})
            
            # Test key derivation
            self.log.info("Testing key derivation...")
            success = crypto.initialize_master_key(test_password)
            if not success:
                self.log.failure("Failed to initialize master key")
                self.issues.append("CryptoController failed to initialize master key")
                return False
            
            self.log.success("Master key initialized successfully")
            
            # Test encryption and decryption
            self.log.info("Testing encryption and decryption...")
            
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(delete=False) as temp_in:
                temp_in.write(b"Test encryption content")
                input_path = temp_in.name
            
            output_path = input_path + ".encrypted"
            decrypted_path = input_path + ".decrypted"
            
            try:
                # Encrypt
                self.log.info(f"Encrypting: {input_path} -> {output_path}")
                crypto.encrypt_file(input_path, output_path)
                
                if not Path(output_path).exists():
                    self.log.failure("Encrypted file was not created")
                    self.issues.append("CryptoController failed to create encrypted file")
                    return False
                
                # Decrypt
                self.log.info(f"Decrypting: {output_path} -> {decrypted_path}")
                crypto.decrypt_file(output_path, decrypted_path)
                
                if not Path(decrypted_path).exists():
                    self.log.failure("Decrypted file was not created")
                    self.issues.append("CryptoController failed to create decrypted file")
                    return False
                
                # Verify content
                with open(input_path, 'rb') as f_in, open(decrypted_path, 'rb') as f_out:
                    input_content = f_in.read()
                    output_content = f_out.read()
                
                if input_content == output_content:
                    self.log.success("Encryption/decryption test passed")
                else:
                    self.log.failure("Decrypted content does not match original")
                    self.issues.append("CryptoController decryption failed to restore original content")
                    return False
            
            finally:
                # Clean up temp files
                for path in [input_path, output_path, decrypted_path]:
                    if os.path.exists(path):
                        os.unlink(path)
            
            # Success
            self.crypto = crypto
            self.crypto_success = True
            
            self.log.result("CryptoController Tests", True)
            return True
            
        except Exception as e:
            self.log.error(f"Error in CryptoController tests: {e}", exc_info=True)
            self.issues.append(f"Error in CryptoController tests: {str(e)}")
            self.crypto_success = False
            return False
    
    def test_vault_manager(self) -> bool:
        """Test VaultManager functionality"""
        self.log.step("Testing VaultManager")
        
        if 'vault_manager' not in self.modules or not self.crypto:
            self.log.error("VaultManager module not available or CryptoController test failed")
            return False
        
        VaultManager = self.modules['vault_manager']
        
        try:
            # Create temp directory for test vault
            test_vault_dir = Path(tempfile.mkdtemp())
            self.log.info(f"Created test vault directory: {test_vault_dir}")
            
            try:
                # Create vault manager instance
                self.log.info("Creating VaultManager instance")
                vault_manager = VaultManager(test_vault_dir, self.crypto)
                
                # Test vault creation
                self.log.info("Testing vault creation...")
                success = vault_manager.create_vault()
                if not success:
                    self.log.failure("Failed to create vault")
                    self.issues.append("VaultManager failed to create vault")
                    return False
                
                self.log.success("Vault created successfully")
                
                # Check vault structure
                self.log.info("Checking vault structure...")
                vault_config = test_vault_dir / 'vault.config'
                vault_key = test_vault_dir / 'vault.key'
                
                if not vault_config.exists() or not vault_key.exists():
                    self.log.failure("Vault structure is incomplete")
                    self.issues.append("VaultManager created incomplete vault structure")
                    return False
                
                # Test vault_exists
                self.log.info("Testing vault existence check...")
                exists = vault_manager.vault_exists()
                if not exists:
                    self.log.failure("vault_exists() returned False for newly created vault")
                    self.issues.append("VaultManager.vault_exists() failed to detect existing vault")
                    return False
                
                self.log.success("Vault existence check passed")
                
                # Success
                self.vault_manager = vault_manager
                self.vault_manager_success = True
                
                self.log.result("VaultManager Tests", True)
                return True
                
            finally:
                # Clean up temp vault
                import shutil
                shutil.rmtree(test_vault_dir, ignore_errors=True)
                
        except Exception as e:
            self.log.error(f"Error in VaultManager tests: {e}", exc_info=True)
            self.issues.append(f"Error in VaultManager tests: {str(e)}")
            self.vault_manager_success = False
            return False
    
    def test_core_engine(self, test_password: str = "test123") -> bool:
        """Test GraphiVaultCore functionality"""
        self.log.step("Testing GraphiVaultCore")
        
        if 'core_engine' not in self.modules:
            self.log.error("GraphiVaultCore module not available")
            return False
        
        GraphiVaultCore = self.modules['core_engine']
        
        try:
            # Create temp directory for test vault
            test_vault_dir = Path(tempfile.mkdtemp())
            self.log.info(f"Created test core vault directory: {test_vault_dir}")
            
            try:
                # Create core engine instance
                self.log.info("Creating GraphiVaultCore instance")
                core = GraphiVaultCore(str(test_vault_dir))
                
                # Test vault initialization
                self.log.info(f"Testing vault initialization with password: {test_password[:2]}***")
                success = core.initialize_vault(test_password)
                if not success:
                    self.log.failure("Failed to initialize vault")
                    self.issues.append("GraphiVaultCore failed to initialize vault")
                    return False
                
                self.log.success("Vault initialized successfully")
                
                # Test vault lock/unlock
                self.log.info("Testing vault locking...")
                lock_success = core.lock_vault()
                if not lock_success:
                    self.log.failure("Failed to lock vault")
                    self.issues.append("GraphiVaultCore failed to lock vault")
                    return False
                
                self.log.success("Vault locked successfully")
                
                # Create new core instance to test unlocking
                self.log.info("Creating new core instance...")
                core = GraphiVaultCore(str(test_vault_dir))
                
                self.log.info(f"Testing vault unlock with password: {test_password[:2]}***")
                unlock_success = core.unlock_vault(test_password)
                if not unlock_success:
                    self.log.failure("Failed to unlock vault")
                    self.issues.append("GraphiVaultCore failed to unlock vault with correct password")
                    return False
                
                self.log.success("Vault unlocked successfully")
                
                # Success
                self.core_engine = core
                self.core_success = True
                
                self.log.result("GraphiVaultCore Tests", True)
                return True
                
            finally:
                # Clean up temp vault
                import shutil
                shutil.rmtree(test_vault_dir, ignore_errors=True)
                
        except Exception as e:
            self.log.error(f"Error in GraphiVaultCore tests: {e}", exc_info=True)
            self.issues.append(f"Error in GraphiVaultCore tests: {str(e)}")
            self.core_success = False
            return False
    
    def test_ipc_gateway(self, test_password: str = "test123") -> bool:
        """Test IPCGateway functionality"""
        self.log.step("Testing IPCGateway")
        
        if 'ipc_gateway' not in self.modules:
            self.log.error("IPCGateway module not available")
            return False
        
        IPCGateway = self.modules['ipc_gateway']
        
        try:
            # Create temp directory for test vault
            test_vault_dir = Path(tempfile.mkdtemp())
            self.log.info(f"Created test IPC vault directory: {test_vault_dir}")
            
            try:
                # Create IPC gateway instance
                self.log.info("Creating IPCGateway instance")
                gateway = IPCGateway(str(test_vault_dir))
                
                # Test vault initialization
                self.log.info(f"Testing vault initialization with password: {test_password[:2]}***")
                init_result = gateway.initialize_vault(test_password)
                
                if not init_result.get('success', False):
                    self.log.failure(f"Failed to initialize vault: {init_result.get('error', 'Unknown error')}")
                    self.issues.append(f"IPCGateway failed to initialize vault: {init_result.get('error')}")
                    return False
                
                self.log.success("Vault initialized successfully via IPC")
                
                # Test vault status
                self.log.info("Testing vault status check...")
                status_result = gateway.get_vault_status()
                
                if not status_result.get('success', False):
                    self.log.failure(f"Failed to get vault status: {status_result.get('error', 'Unknown error')}")
                    self.issues.append(f"IPCGateway failed to get vault status: {status_result.get('error')}")
                    return False
                
                self.log.success(f"Vault status check successful: {status_result}")
                
                # Test vault unlock
                self.log.info("Testing vault lock and unlock...")
                
                # Lock vault first
                lock_result = gateway.lock_vault()
                if not lock_result.get('success', False):
                    self.log.failure(f"Failed to lock vault: {lock_result.get('error', 'Unknown error')}")
                    self.issues.append(f"IPCGateway failed to lock vault: {lock_result.get('error')}")
                    return False
                
                self.log.success("Vault locked successfully via IPC")
                
                # Unlock vault
                unlock_result = gateway.unlock_vault(test_password)
                if not unlock_result.get('success', False):
                    self.log.failure(f"Failed to unlock vault: {unlock_result.get('error', 'Unknown error')}")
                    self.issues.append(f"IPCGateway failed to unlock vault: {unlock_result.get('error')}")
                    return False
                
                self.log.success("Vault unlocked successfully via IPC")
                
                # Success
                self.ipc_gateway = gateway
                self.ipc_success = True
                
                self.log.result("IPCGateway Tests", True)
                return True
                
            finally:
                # Clean up temp vault
                import shutil
                shutil.rmtree(test_vault_dir, ignore_errors=True)
                
        except Exception as e:
            self.log.error(f"Error in IPCGateway tests: {e}", exc_info=True)
            self.issues.append(f"Error in IPCGateway tests: {str(e)}")
            self.ipc_success = False
            return False
    
    def test_real_vault(self, vault_path: Path, test_password: str = "test123") -> bool:
        """Test operations on a real vault"""
        self.log.step(f"Testing Real Vault at {vault_path}")
        
        if 'ipc_gateway' not in self.modules:
            self.log.error("IPCGateway module not available")
            return False
        
        IPCGateway = self.modules['ipc_gateway']
        
        try:
            # Validate vault structure first
            validator = VaultValidator(vault_path, self.log)
            if not validator.validate_structure():
                self.log.warning("Skipping real vault test due to invalid structure")
                return False
            
            # Create IPC gateway instance
            self.log.info("Creating IPCGateway instance for real vault")
            gateway = IPCGateway(str(vault_path))
            
            # Check vault status
            self.log.info("Checking vault status...")
            status_result = gateway.get_vault_status()
            
            if not status_result.get('success', False):
                self.log.failure(f"Failed to get vault status: {status_result.get('error', 'Unknown error')}")
                self.issues.append(f"Failed to get real vault status: {status_result.get('error')}")
                return False
            
            self.log.success(f"Vault status check successful")
            self.log.info(f"Vault status: {status_result}")
            
            # Test unlocking with the provided password
            self.log.info(f"Testing vault unlock with password: {test_password[:2]}***")
            unlock_result = gateway.unlock_vault(test_password)
            
            if not unlock_result.get('success', False):
                error_msg = unlock_result.get('error', 'Unknown error')
                traceback_data = unlock_result.get('traceback', '')
                
                self.log.failure(f"Failed to unlock vault: {error_msg}")
                if traceback_data:
                    self.log.error(f"Traceback: {traceback_data}")
                    
                self.issues.append(f"Failed to unlock real vault: {error_msg}")
                return False
            
            self.log.success("Vault unlocked successfully")
            
            # Test getting a list of images
            try:
                from storage.storage_interface import StorageInterface
                
                db_path = vault_path / 'database' / 'vault.db'
                if not db_path.exists():
                    self.log.warning(f"Database file not found: {db_path}")
                    return False
                
                self.log.info(f"Connecting to database: {db_path}")
                storage = StorageInterface(str(db_path), gateway.core.crypto)
                
                self.log.info("Retrieving image list...")
                images = storage.get_all_images()
                
                self.log.success(f"Retrieved {len(images)} images from vault")
                
                return True
                
            except Exception as e:
                self.log.error(f"Error accessing vault data: {e}", exc_info=True)
                self.issues.append(f"Error accessing vault data: {str(e)}")
                return False
            
        except Exception as e:
            self.log.error(f"Error testing real vault: {e}", exc_info=True)
            self.issues.append(f"Error testing real vault: {str(e)}")
            return False
    
    def run_all_tests(self, test_password: str = "test123") -> bool:
        """Run all backend tests"""
        self.log.section("Starting GraphiVault Backend Test Suite")
        
        # Import modules first
        if not self.import_backend_modules():
            self.log.warning("Skipping remaining tests due to import failures")
            return False
        
        # Run individual component tests
        crypto_success = self.test_crypto_controller(test_password)
        vault_manager_success = False
        core_success = False
        ipc_success = False
        
        # Only continue if crypto test passes
        if crypto_success:
            vault_manager_success = self.test_vault_manager()
            core_success = self.test_core_engine(test_password)
            ipc_success = self.test_ipc_gateway(test_password)
        
        # Test the real vault
        real_vault_success = self.test_real_vault(self.vault_path, test_password)
        
        # Overall assessment
        overall_success = (
            crypto_success and
            vault_manager_success and
            core_success and
            ipc_success
        )
        
        # Print summary
        self.log.section("Test Summary")
        self.log.info(f"CryptoController Tests: {crypto_success}")
        self.log.info(f"VaultManager Tests: {vault_manager_success}")
        self.log.info(f"GraphiVaultCore Tests: {core_success}")
        self.log.info(f"IPCGateway Tests: {ipc_success}")
        self.log.info(f"Real Vault Tests: {real_vault_success}")
        
        if self.issues:
            self.log.info(f"\nIssues Found ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                self.log.warning(f"{i}. {issue}")
        
        self.log.result("Overall Test Suite", overall_success)
        
        return overall_success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='GraphiVault Backend Tester')
    parser.add_argument('--vault-path', type=str, default='../test_vault',
                        help='Path to the vault directory')
    parser.add_argument('--password', type=str, default='test123',
                        help='Password to test vault unlocking')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--log-file', type=str,
                        help='Log file path')
    
    args = parser.parse_args()
    
    # Setup logger
    log = DiagnosticLogger(verbose=args.verbose, debug=args.debug)
    log_dir = Path(__file__).parent / 'logs'
    log.setup_file_logging(log_dir, args.log_file)
    
    # Convert relative path to absolute if needed
    vault_path = Path(args.vault_path)
    if not vault_path.is_absolute():
        script_dir = Path(__file__).parent
        vault_path = (script_dir / vault_path).resolve()
    
    # Run tests
    tester = BackendTester(
        vault_path=vault_path,
        log=log
    )
    
    success = tester.run_all_tests(args.password)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
