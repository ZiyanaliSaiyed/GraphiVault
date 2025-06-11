#!/usr/bin/env python3
"""
GraphiVault Database Initialization
Handles vault creation, database setup, and initial configuration
"""

import os
import sqlite3
import secrets
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

try:
    from .crypto_controller import CryptoController
    from .storage_interface import StorageInterface
except ImportError:
    from crypto_controller import CryptoController
    from storage_interface import StorageInterface


class DatabaseInitializer:
    """
    Database Initializer - Creates and configures GraphiVault databases
    
    Features:
    - Vault directory creation
    - Database initialization with proper schema
    - Cryptographic salt generation
    - Initial metadata setup
    - Security configuration
    """
    
    def __init__(self, vault_path: str):
        """Initialize database initializer"""
        self.vault_path = Path(vault_path)
        self.db_path = self.vault_path / "data" / "graphivault.db"
        
    def create_vault_structure(self) -> bool:
        """Create the vault directory structure"""
        try:
            # Create main vault directory
            self.vault_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.vault_path / "data").mkdir(exist_ok=True)
            (self.vault_path / "encrypted").mkdir(exist_ok=True)
            (self.vault_path / "thumbnails").mkdir(exist_ok=True)
            (self.vault_path / "temp").mkdir(exist_ok=True)
            (self.vault_path / "backups").mkdir(exist_ok=True)
            
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            return True
            
        except Exception as e:
            print(f"Error creating vault structure: {e}")
            return False
    
    def initialize_vault(self, master_password: str) -> bool:
        """Initialize a new vault with database and crypto setup"""
        try:
            # Create vault directory structure
            if not self.create_vault_structure():
                return False
            
            # Initialize crypto controller
            crypto = CryptoController({})
            if not crypto.initialize_master_key(master_password):
                return False
            
            # Initialize storage interface (this creates the database)
            storage = StorageInterface(str(self.db_path), crypto)
            
            # Set initial vault configuration
            vault_id = secrets.token_hex(16)
            vault_salt = secrets.token_hex(32)
            creation_time = datetime.now(timezone.utc).isoformat()
            
            # Store vault metadata
            storage.set_vault_meta("vault_id", vault_id)
            storage.set_vault_meta("vault_name", f"GraphiVault_{vault_id[:8]}")
            storage.set_vault_meta("created_at", creation_time)
            storage.set_vault_meta("last_opened", creation_time)
            storage.set_vault_meta("version", "1.0.0")
            storage.set_vault_meta("encryption_version", "1")
            
            # Log vault creation
            storage.log_auth_event("vault_created", "success", f"Vault created at {self.vault_path}")
            
            # Perform sanity check
            if not self._sanity_check(storage):
                return False
            
            storage.close()
            crypto.clear_keys()
            
            print(f"✓ Vault created successfully at: {self.vault_path}")
            return True
            
        except Exception as e:
            print(f"Error initializing vault: {e}")
            return False
    
    def _sanity_check(self, storage: StorageInterface) -> bool:
        """Perform database sanity check"""
        try:
            # Test basic operations
            test_key = "sanity_check"
            test_value = "test_" + secrets.token_hex(8)
            
            # Test write
            if not storage.set_vault_meta(test_key, test_value):
                return False
            
            # Test read
            retrieved_value = storage.get_vault_meta(test_key)
            if retrieved_value != test_value:
                return False
            
            # Test auth logging
            if not storage.log_auth_event("sanity_check", "success", "Database sanity check passed"):
                return False
            
            # Clean up test data
            storage._get_connection().execute("DELETE FROM vault_meta WHERE key = ?", (test_key,))
            storage._get_connection().commit()
            
            return True
            
        except Exception as e:
            print(f"Sanity check failed: {e}")
            return False
    
    def check_vault_exists(self) -> bool:
        """Check if vault already exists"""
        return self.db_path.exists() and self.vault_path.exists()
    
    def get_vault_info(self) -> Optional[dict]:
        """Get basic vault information"""
        if not self.check_vault_exists():
            return None
        
        try:
            # Create temporary storage interface for reading metadata
            dummy_crypto = CryptoController({})
            storage = StorageInterface(str(self.db_path), dummy_crypto)
            
            vault_info = {
                "vault_id": storage.get_vault_meta("vault_id"),
                "vault_name": storage.get_vault_meta("vault_name"),
                "created_at": storage.get_vault_meta("created_at"),
                "last_opened": storage.get_vault_meta("last_opened"),
                "version": storage.get_vault_meta("version"),
                "path": str(self.vault_path),
                "db_size": self.db_path.stat().st_size if self.db_path.exists() else 0
            }
            
            storage.close()
            return vault_info
            
        except Exception as e:
            print(f"Error getting vault info: {e}")
            return None
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            if not self.db_path.exists():
                return False
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use SQLite backup API
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            backup_conn.close()
            source_conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False


def create_vault(vault_path: str, master_password: str) -> bool:
    """Convenience function to create a new vault"""
    initializer = DatabaseInitializer(vault_path)
    return initializer.initialize_vault(master_password)


def check_vault(vault_path: str) -> Optional[dict]:
    """Convenience function to check vault status"""
    initializer = DatabaseInitializer(vault_path)
    return initializer.get_vault_info()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python database_init.py <vault_path> <master_password>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    master_password = sys.argv[2]
    
    if create_vault(vault_path, master_password):
        print("Vault created successfully!")
        
        # Show vault info
        info = check_vault(vault_path)
        if info:
            print(f"Vault ID: {info['vault_id']}")
            print(f"Vault Name: {info['vault_name']}")
            print(f"Created: {info['created_at']}")
    else:
        print("Failed to create vault!")
        sys.exit(1)
