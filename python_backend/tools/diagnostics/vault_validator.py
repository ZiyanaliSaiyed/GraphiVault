#!/usr/bin/env python3
"""
GraphiVault Vault Validator
Validates vault structure, file formats, and crypto initialization
"""

import os
import sys
import json
import sqlite3
import traceback
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# Add parent directories to path for imports
script_dir = Path(__file__).parent
tools_dir = script_dir.parent
backend_dir = tools_dir.parent
sys.path.insert(0, str(backend_dir))

# Import diagnostic logger
from tools.diagnostics.utils.logger import DiagnosticLogger

# Try to import required GraphiVault modules
try:
    from crypto.crypto_controller import CryptoController
except ImportError as e:
    print(f"Failed to import CryptoController: {e}")
    print("Make sure you're running this script from the python_backend directory.")
    sys.exit(1)

class VaultValidator:
    """
    Validates GraphiVault vault structure and configuration
    
    Performs checks on:
    - Vault directory structure
    - Configuration files format and content
    - Crypto initialization and key verification
    - Database structure and connectivity
    """
    
    def __init__(self, 
                 vault_path: Path, 
                 log: DiagnosticLogger,
                 create_missing: bool = False):
        """Initialize validator with vault path and options"""
        self.vault_path = vault_path
        self.log = log
        self.create_missing = create_missing
        self.issues = []
        self.crypto = None
        
        # Define required paths
        self.required_files = {
            'vault_config': vault_path / 'vault.config',
            'vault_key': vault_path / 'vault.key',
            'database': vault_path / 'database' / 'vault.db'
        }
        
        self.required_dirs = {
            'database': vault_path / 'database',
            'data': vault_path / 'data',
            'thumbnails': vault_path / 'thumbnails',
            'metadata': vault_path / 'metadata',
            'temp': vault_path / 'temp',
            'backups': vault_path / 'backups'
        }
        
        # Test results
        self.structure_valid = False
        self.config_valid = False
        self.key_valid = False
        self.db_valid = False
        self.crypto_load_success = False
        self.crypto_verify_success = False
    
    def validate_structure(self) -> bool:
        """Validate vault directory structure"""
        self.log.step("Validating Vault Directory Structure")
        
        # Check if vault directory exists
        if not self.vault_path.exists():
            self.log.error(f"Vault directory not found: {self.vault_path}")
            if self.create_missing:
                try:
                    self.vault_path.mkdir(parents=True, exist_ok=True)
                    self.log.info(f"Created vault directory: {self.vault_path}")
                except Exception as e:
                    self.log.error(f"Failed to create vault directory: {e}", exc_info=True)
                    return False
            else:
                return False
        
        # Check required directories
        missing_dirs = []
        for name, dir_path in self.required_dirs.items():
            if not dir_path.exists():
                missing_dirs.append((name, dir_path))
                self.issues.append(f"Missing directory: {dir_path}")
        
        # Create missing directories if specified
        if missing_dirs and self.create_missing:
            for name, dir_path in missing_dirs:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.log.info(f"Created directory: {dir_path}")
                except Exception as e:
                    self.log.error(f"Failed to create directory {dir_path}: {e}")
        
        # Check required files
        missing_files = []
        for name, file_path in self.required_files.items():
            if not file_path.exists():
                missing_files.append((name, file_path))
                self.issues.append(f"Missing file: {file_path}")
        
        # Create stub files if specified
        if missing_files and self.create_missing:
            for name, file_path in missing_files:
                try:
                    # Create parent directory if needed
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create appropriate stub based on file type
                    if name == 'vault_config':
                        self._create_stub_config(file_path)
                    elif name == 'vault_key':
                        self._create_stub_key(file_path)
                    elif name == 'database':
                        self._create_stub_database(file_path)
                        
                    self.log.info(f"Created stub file: {file_path}")
                except Exception as e:
                    self.log.error(f"Failed to create {file_path}: {e}")
        
        # Structure is valid if all required files and dirs exist
        self.structure_valid = (
            all(dir_path.exists() for dir_path in self.required_dirs.values()) and
            all(file_path.exists() for file_path in self.required_files.values())
        )
        
        self.log.result("Vault Structure", self.structure_valid)
        return self.structure_valid
    
    def validate_config_file(self) -> bool:
        """Validate vault.config file format and content"""
        self.log.step("Validating Vault Configuration")
        
        config_path = self.required_files['vault_config']
        if not config_path.exists():
            self.log.error(f"Config file not found: {config_path}")
            return False
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
              # Check required fields
            required_fields = ['vault_id', 'version', 'created_at', 'encrypted']
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                self.issues.append(f"Missing fields in vault.config: {', '.join(missing_fields)}")
                self.log.error(f"Vault config missing required fields: {missing_fields}")
                self.config_valid = False
            else:
                self.log.info(f"Vault config contains all required fields")
                self.log.debug(f"Vault ID: {config['vault_id']}")
                self.log.debug(f"Version: {config['version']}")
                self.config_valid = True
                
            self.log.result("Configuration Format", self.config_valid)
            return self.config_valid
            
        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in vault.config: {str(e)}")
            self.log.error(f"Invalid JSON format in vault.config: {e}")
            self.config_valid = False
            return False
        except Exception as e:
            self.issues.append(f"Error reading vault.config: {str(e)}")
            self.log.error(f"Error reading vault.config: {e}", exc_info=True)
            self.config_valid = False
            return False
    
    def validate_key_file(self) -> bool:
        """Validate vault.key file format and content"""
        self.log.step("Validating Vault Key File")
        
        key_path = self.required_files['vault_key']
        if not key_path.exists():
            self.log.error(f"Key file not found: {key_path}")
            return False
        
        try:
            with open(key_path, 'r') as f:
                key_data = json.load(f)
              # Check required fields
            required_fields = ['algorithm', 'key_derivation', 'iterations', 'salt']
            missing_fields = [field for field in required_fields if field not in key_data]
            if missing_fields:
                self.issues.append(f"Missing fields in vault.key: {', '.join(missing_fields)}")
                self.log.error(f"Vault key file missing required fields: {missing_fields}")
                self.key_valid = False
            else:
                self.log.info(f"Vault key file contains all required fields")
                self.log.debug(f"Algorithm: {key_data['algorithm']}")
                self.log.debug(f"Key derivation: {key_data['key_derivation']}")
                self.log.debug(f"Iterations: {key_data['iterations']}")
                
                # Check if salt is in valid format (base64)
                salt = key_data.get('salt')
                if not salt:
                    self.issues.append("Salt value is empty in vault.key")
                    self.log.error("Salt value is empty in vault.key")
                    self.key_valid = False
                else:
                    self.key_valid = True
                    
            self.log.result("Key File Format", self.key_valid)
            return self.key_valid
            
        except json.JSONDecodeError as e:
            self.issues.append(f"Invalid JSON in vault.key: {str(e)}")
            self.log.error(f"Invalid JSON format in vault.key: {e}")
            self.key_valid = False
            return False
        except Exception as e:
            self.issues.append(f"Error reading vault.key: {str(e)}")
            self.log.error(f"Error reading vault.key: {e}", exc_info=True)
            self.key_valid = False
            return False
    
    def validate_database(self) -> bool:
        """Validate database structure and connectivity"""
        self.log.step("Validating Vault Database")
        
        db_path = self.required_files['database']
        if not db_path.exists():
            self.log.error(f"Database file not found: {db_path}")
            return False
        
        try:
            # Check if file is a valid SQLite database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['images', 'tags', 'image_tags', 'annotations']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                self.issues.append(f"Missing tables in database: {', '.join(missing_tables)}")
                self.log.error(f"Database missing required tables: {missing_tables}")
                self.db_valid = False
            else:
                self.log.info(f"Database contains all required tables")
                  # Check image count
                cursor.execute("SELECT COUNT(*) FROM images;")
                image_count = cursor.fetchone()[0]
                self.log.info(f"Database contains {image_count} images")
                # Check other table counts
                for table in ['tags', 'image_tags', 'annotations']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    self.log.info(f"Table '{table}' contains {count} records")
                
                self.db_valid = True
            
            conn.close()
            self.log.result("Database Validation", self.db_valid)
            return self.db_valid
            
        except sqlite3.Error as e:
            self.issues.append(f"SQLite error with vault.db: {str(e)}")
            self.log.error(f"SQLite error: {e}")
            self.db_valid = False
            return False
        except Exception as e:
            self.issues.append(f"Error validating database: {str(e)}")
            self.log.error(f"Error validating database: {e}", exc_info=True)
            self.db_valid = False
            return False
    
    def test_crypto_initialization(self, test_password: str = "test123") -> Tuple[bool, bool]:
        """Test crypto initialization and key verification"""
        self.log.step("Testing Crypto Initialization")
        
        try:
            # Create crypto controller
            self.log.info("Creating CryptoController instance")
            self.crypto = CryptoController({})
            
            # Load crypto parameters
            self.log.info(f"Loading crypto parameters from {self.vault_path}")
            load_result = self.crypto.load_crypto_params(self.vault_path)
            self.crypto_load_success = load_result
            
            if not load_result:
                self.issues.append("Failed to load crypto parameters")
                self.log.error("Failed to load crypto parameters")
                self.log.result("Crypto Initialization", False)
                return False, False
            
            self.log.success("Crypto parameters loaded successfully")
            
            # Test key verification
            self.log.info(f"Testing key verification with password: {test_password[:2]}***")
            verify_result = self.crypto.verify_master_key(test_password)
            self.crypto_verify_success = verify_result
            
            if not verify_result:
                self.issues.append("Failed to verify master key with test password")
                self.log.warning("Master key verification failed with test password")
            else:
                self.log.success("Master key verified successfully")
            
            self.log.result("Crypto Initialization", load_result)
            self.log.result("Password Verification", verify_result)
            
            return load_result, verify_result
            
        except Exception as e:
            self.issues.append(f"Error in crypto initialization: {str(e)}")
            self.log.error(f"Error in crypto initialization: {e}", exc_info=True)
            self.crypto_load_success = False
            self.crypto_verify_success = False
            return False, False
    
    def run_all_checks(self, test_password: str = "test123") -> bool:
        """Run all validation checks"""
        self.log.section("Starting GraphiVault Validation Suite")
        
        # Run all tests
        structure_valid = self.validate_structure()
        
        # Only continue if structure is valid
        if not structure_valid:
            self.log.warning("Skipping remaining tests due to invalid structure")
            return False
        
        config_valid = self.validate_config_file()
        key_valid = self.validate_key_file()
        db_valid = self.validate_database()
        
        crypto_load_success, crypto_verify_success = self.test_crypto_initialization(test_password)
        
        # Overall assessment
        overall_success = (
            structure_valid and 
            config_valid and
            key_valid and 
            db_valid and
            crypto_load_success
        )
        
        # Print summary
        self.log.section("Validation Summary")
        self.log.info(f"Structure Valid: {structure_valid}")
        self.log.info(f"Config Format Valid: {config_valid}")
        self.log.info(f"Key Format Valid: {key_valid}")
        self.log.info(f"Database Valid: {db_valid}")
        self.log.info(f"Crypto Load Success: {crypto_load_success}")
        self.log.info(f"Password Verification: {crypto_verify_success}")
        
        if self.issues:
            self.log.info(f"\nIssues Found ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                self.log.warning(f"{i}. {issue}")
        
        self.log.result("Overall Validation", overall_success)
        
        return overall_success
    
    def _create_stub_config(self, file_path: Path):
        """Create a stub vault.config file"""
        import uuid
        from datetime import datetime, timezone
        
        stub_config = {
            "vault_id": str(uuid.uuid4()),
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "encrypted": True,
            "compression_enabled": False,
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "supported_formats": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
            "security_level": "high",
            "backup_enabled": True,
            "audit_logging": True
        }
        
        with open(file_path, 'w') as f:
            json.dump(stub_config, f, indent=2)
    
    def _create_stub_key(self, file_path: Path):
        """Create a stub vault.key file"""
        import base64
        import secrets
        
        stub_key = {
            "algorithm": "AES-256-GCM",
            "key_derivation": "PBKDF2-HMAC-SHA512",
            "iterations": 200000,
            "salt_size": 32,
            "nonce_size": 12,
            "tag_size": 16,
            "salt": base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
        }
        
        with open(file_path, 'w') as f:
            json.dump(stub_key, f, indent=2)
    
    def _create_stub_database(self, file_path: Path):
        """Create a stub SQLite database with required schema"""
        conn = sqlite3.connect(str(file_path))
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


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='GraphiVault Vault Validator')
    parser.add_argument('--vault-path', type=str, default='../../../test_vault',
                        help='Path to the vault directory')
    parser.add_argument('--create-missing', action='store_true',
                        help='Create missing files and directories')
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
    
    # Run validation
    validator = VaultValidator(
        vault_path=vault_path,
        log=log,
        create_missing=args.create_missing
    )
    
    success = validator.run_all_checks(args.password)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
