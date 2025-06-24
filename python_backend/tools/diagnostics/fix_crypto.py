#!/usr/bin/env python3
"""
GraphiVault Crypto Fix Script
Fixes issues with CryptoController's load_crypto_params method
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import diagnostic logger
from diagnostics.utils.logger import DiagnosticLogger


def fix_crypto_controller(log: DiagnosticLogger) -> bool:
    """
    Fix issues in the CryptoController implementation
    
    Specifically, fixes the load_crypto_params method to properly
    initialize the master key from the stored parameters
    """
    log.section("Fixing CryptoController Implementation")
    
    crypto_file = parent_dir / 'crypto' / 'crypto_controller.py'
    if not crypto_file.exists():
        log.error(f"CryptoController file not found: {crypto_file}")
        return False
    
    log.info(f"Opening file: {crypto_file}")
    
    try:
        with open(crypto_file, 'r') as f:
            content = f.read()
        
        # Find the load_crypto_params method
        load_params_start = content.find("def load_crypto_params")
        if load_params_start == -1:
            log.error("Could not find load_crypto_params method")
            return False
        
        load_params_end = content.find("def", load_params_start + 1)
        if load_params_end == -1:
            log.error("Could not find the end of load_crypto_params method")
            return False
        
        load_params_code = content[load_params_start:load_params_end]
        
        # Check if the method already initializes _master_key
        if "_master_key = " in load_params_code:
            log.info("CryptoController.load_crypto_params already initializes master key")
            return True
        
        # Find the line that sets the salt
        salt_line_idx = load_params_code.find("self._key_derivation_salt = base64.b64decode")
        if salt_line_idx == -1:
            log.error("Could not find salt initialization code")
            return False
        
        # Find the end of the method body
        method_body_end = load_params_code.rfind("return True")
        if method_body_end == -1:
            log.error("Could not find the end of the method body")
            return False
          # Create the code to add
        code_to_add = """
            # Fix: Initialize master key from stored parameters if password is not supplied
            # This is a temporary fix that will be called when verify_master_key is used
            # In a real implementation, this would require the password to be supplied
            
            # Test if salt was loaded successfully
            if self._key_derivation_salt:
                try:
                    # Import required modules
                    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
                    from cryptography.hazmat.primitives import hashes
                    from cryptography.hazmat.backends import default_backend
                    
                    # Create a key derivation function
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA512(),
                        length=32,
                        salt=self._key_derivation_salt,
                        iterations=self.config['iterations'],
                        backend=default_backend()
                    )
                    
                    # Securely prompt for the test password instead of hardcoding it
                    import getpass
                    test_password = getpass.getpass("Enter the test password to derive the key: ").encode('utf-8')
                    self._master_key = kdf.derive(test_password)
                    print("CryptoController: Derived master key from provided password")
                except Exception as e:
                    print(f"CryptoController: Failed to derive master key: {e}")
                    self._master_key = None
            else:
                print("CryptoController: No salt available, using placeholder key")
                self._master_key = b'PLACEHOLDER_KEY_FOR_TEST123'
                
            # WARNING: This is NOT secure and is only for diagnostic purposes!
            """
        
        # Insert the code before the return statement
        new_method_code = load_params_code[:method_body_end] + code_to_add + load_params_code[method_body_end:]
        
        # Replace the method in the full content
        new_content = content[:load_params_start] + new_method_code + content[load_params_end:]
        
        # Backup the original file
        backup_file = crypto_file.with_suffix('.py.bak')
        with open(backup_file, 'w') as f:
            f.write(content)
        log.info(f"Created backup: {backup_file}")
        
        # Write the modified file
        with open(crypto_file, 'w') as f:
            f.write(new_content)
        log.success(f"Updated CryptoController: {crypto_file}")
        
        return True
        
    except Exception as e:
        log.error(f"Error fixing CryptoController: {e}", exc_info=True)
        return False


def create_test_vault_stubs(vault_path: Path, log: DiagnosticLogger) -> bool:
    """
    Create test vault stubs for easier testing
    """
    log.section("Creating Test Vault Stubs")
    
    try:
        # Create vault directory
        vault_path.mkdir(parents=True, exist_ok=True)
        log.info(f"Created vault directory: {vault_path}")
        
        # Create required subdirectories
        for subdir in ['data', 'thumbnails', 'metadata', 'temp', 'backups', 'database']:
            dir_path = vault_path / subdir
            dir_path.mkdir(exist_ok=True)
            log.info(f"Created directory: {dir_path}")
        
        # Create vault.config
        config_path = vault_path / 'vault.config'
        vault_config = {
            "vault_id": "test-vault-123456789",
            "version": "1.0.0",
            "created_at": "2025-06-18T10:00:00Z",
            "encrypted": True,
            "compression_enabled": False,
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "supported_formats": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
            "security_level": "high",
            "backup_enabled": True,
            "audit_logging": True
        }
        
        with open(config_path, 'w') as f:
            json.dump(vault_config, f, indent=2)
        log.info(f"Created config file: {config_path}")
        
        # Create vault.key
        key_path = vault_path / 'vault.key'
        
        # This should match the expected salt for password "test123"
        # In a real system, this would be randomly generated
        salt_bytes = b'ThisIsATestSaltForTheTestPasswordTest123'
        
        vault_key = {
            "algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2-HMAC-SHA512",
            "iterations": 200000,
            "salt_size": 32,
            "nonce_size": 12,
            "tag_size": 16,
            "salt": base64.b64encode(salt_bytes).decode('utf-8')
        }
        
        with open(key_path, 'w') as f:
            json.dump(vault_key, f, indent=2)
        log.info(f"Created key file: {key_path}")
        
        # Create stub SQLite database
        import sqlite3
        db_path = vault_path / 'database' / 'vault.db'
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            file_name TEXT NOT NULL,
            storage_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            is_deleted BOOLEAN DEFAULT 0
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            tag_type TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            FOREIGN KEY (image_id) REFERENCES images (id),
            FOREIGN KEY (tag_id) REFERENCES tags (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (image_id) REFERENCES images (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        log.info(f"Created database: {db_path}")
        
        # Create audit log file
        audit_path = vault_path / 'audit.log'
        with open(audit_path, 'w') as f:
            f.write("# GraphiVault Audit Log\n")
            f.write("# Created: 2025-06-18T10:00:00Z\n")
        log.info(f"Created audit log: {audit_path}")
        
        return True
        
    except Exception as e:
        log.error(f"Error creating test vault stubs: {e}", exc_info=True)
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='GraphiVault Backend Fix Script')
    parser.add_argument('--vault-path', type=str, default='../../test_vault',
                        help='Path to create test vault stubs')
    parser.add_argument('--fix-crypto', action='store_true',
                        help='Fix CryptoController implementation')
    parser.add_argument('--create-stubs', action='store_true',
                        help='Create test vault stubs')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug output')
    
    args = parser.parse_args()
    
    # Setup logger
    log = DiagnosticLogger(verbose=args.verbose, debug=args.debug)
    
    # Convert relative path to absolute if needed
    vault_path = Path(args.vault_path)
    if not vault_path.is_absolute():
        script_dir = Path(__file__).parent
        vault_path = (script_dir / vault_path).resolve()
    
    # Run selected fixes
    success = True
    
    if args.fix_crypto:
        crypto_success = fix_crypto_controller(log)
        success = success and crypto_success
    
    if args.create_stubs:
        stubs_success = create_test_vault_stubs(vault_path, log)
        success = success and stubs_success
    
    if not args.fix_crypto and not args.create_stubs:
        log.info("No actions specified. Use --fix-crypto or --create-stubs.")
        log.info("Use -h for help.")
    
    log.section("Fix Summary")
    log.result("Fix Script", success)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
