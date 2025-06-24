#!/usr/bin/env python3
"""
GraphiVault Core Engine
The heart of the secure image vault system - handles all core operations
with privacy-first, security-by-design principles.
"""

import os
import uuid
import hashlib
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json

try:
    from ..crypto.crypto_controller import CryptoController
    from .vault_manager import VaultManager
    from ..ui.image_processor import ImageProcessor
    from ..utils.tag_manager import TagManager
    from ..database.search_engine import SearchEngine
    from ..utils.audit_logger import AuditLogger
    from .session_manager import SessionManager
    from ..storage.storage_interface import StorageInterface, ImageRecord
except ImportError:
    # Fallback for direct execution
    from crypto.crypto_controller import CryptoController
    from core.vault_manager import VaultManager
    from ui.image_processor import ImageProcessor
    from utils.tag_manager import TagManager
    from database.search_engine import SearchEngine
    from utils.audit_logger import AuditLogger
    from core.session_manager import SessionManager
    from storage.storage_interface import StorageInterface, ImageRecord


# Remove the duplicate ImageRecord definition since it's now imported
# @dataclass
# class ImageRecord:
#     """Secure image record with encrypted metadata"""
#     ...existing definition moved to storage_interface.py...


class GraphiVaultCore:
    """
    Core Engine - The bulletproof fortress of GraphiVault
    
    Implements the 4 unshakable pillars:
    - Privacy-First: No external calls, no backdoors
    - Security-by-Design: Every operation assumes hostile environment
    - Modular Logic: Clean separation, testable components
    - Offline-Optimized: Works forever without internet
    """
    
    def __init__(self, vault_path: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the core engine with secure defaults"""
        self.vault_path = Path(vault_path)
        self.config = config or self._default_config()
          # Initialize modular components
        self.crypto = CryptoController(self.config.get('crypto', {}))
        self.vault_manager = VaultManager(self.vault_path, self.crypto)
        self.image_processor = ImageProcessor(self.config.get('image', {}))
        self.tag_manager = TagManager(self.crypto)
        self.search_engine = SearchEngine()
        self.audit_logger = AuditLogger(self.vault_path / 'audit.log')
        self.session_manager = SessionManager(self.config.get('session', {}))
        
        # Initialize storage interface
        db_path = self.vault_path / 'database' / 'vault.db'
        self.storage = None  # Will be initialized after vault unlock
        
        # Security state
        self._is_initialized = False
        self._master_key_hash = None
        
    def _default_config(self) -> Dict[str, Any]:
        """Default secure configuration"""
        return {
            'crypto': {
                'algorithm': 'AES-256-GCM',
                'key_derivation': 'PBKDF2-HMAC-SHA512',
                'iterations': 200000,  # High iteration count for security
                'salt_size': 32,
                'nonce_size': 12,
                'tag_size': 16
            },
            'image': {
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
                'thumbnail_size': (256, 256),
                'thumbnail_quality': 85
            },
            'session': {
                'timeout_minutes': 30,
                'auto_lock': True,
                'max_failed_attempts': 3
            },
            'vault': {
                'data_dir': 'data',
                'thumbnails_dir': 'thumbnails',
                'temp_dir': 'temp'
            }
        }
    
    def initialize_vault(self, master_password: str) -> bool:
        """
        Initialize a new vault with master password
        Returns True if successful, False otherwise
        """
        try:
            # Audit the initialization attempt
            self.audit_logger.log_event('vault_init_attempt', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'vault_path': str(self.vault_path)
            })
            
            # Create vault structure
            if not self.vault_manager.create_vault():
                return False

            # Initialize crypto with master password
            if not self.crypto.initialize_master_key(master_password, self.vault_path):
                return False

            # Create session
            session_key = self.session_manager.create_session(master_password)
            if not session_key:
                return False
            
            # Initialize storage interface
            db_path = self.vault_path / 'database' / 'vault.db'
            self.storage = StorageInterface(str(db_path), self.crypto)
            
            self._is_initialized = True
            self._master_key_hash = hashlib.sha512(master_password.encode()).hexdigest()
            
            self.audit_logger.log_event('vault_init_success', {
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return True
            
        except Exception as e:
            self.audit_logger.log_event('vault_init_error', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            })
            return False
    
    def unlock_vault(self, master_password: str) -> bool:
        """
        Unlock an existing vault
        Returns True if successful, False otherwise
        """
        try:
            print("🔐 [CORE] Starting vault unlock process...")
            self.audit_logger.log_event('vault_unlock_attempt', {
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Verify vault exists
            if not self.vault_manager.vault_exists():
                print("🔐 [CORE] ERROR: Vault does not exist")
                return False
            print("🔐 [CORE] Vault structure verified")
            
            # Load crypto parameters from storage before verification
            print("🔐 [CORE] Loading crypto parameters...")
            if not self.crypto.load_crypto_params(self.vault_path):
                print("🔐 [CORE] ERROR: Failed to load crypto parameters")
                return False
            print("🔐 [CORE] Crypto parameters loaded successfully")
            
            # Verify master password
            print("🔐 [CORE] Verifying master password...")
            if not self.crypto.verify_master_key(master_password):
                print("🔐 [CORE] ERROR: Master password verification failed")
                self.session_manager.record_failed_attempt()
                return False
            print("🔐 [CORE] Master password verified successfully")              # Create session
            print("🔐 [CORE] Creating session...")
            session_key = self.session_manager.create_session(master_password)
            if not session_key:
                print("🔐 [CORE] ERROR: Failed to create session")
                return False
            print("🔐 [CORE] Session created successfully")
            
            # Initialize storage interface
            print("🔐 [CORE] Initializing storage interface...")
            db_path = self.vault_path / 'database' / 'vault.db'
            self.storage = StorageInterface(str(db_path), self.crypto)
            print("🔐 [CORE] Storage interface initialized")
            
            self._is_initialized = True
            self._master_key_hash = hashlib.sha512(master_password.encode()).hexdigest()
            
            print("🔐 [CORE] Vault unlocked successfully! ✅")
            self.audit_logger.log_event('vault_unlock_success', {
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return True            
        except Exception as e:
            print(f"🔐 [CORE] ERROR: Exception during vault unlock: {str(e)}")
            print(f"🔐 [CORE] Exception type: {type(e).__name__}")
            import traceback
            print(f"🔐 [CORE] Traceback: {traceback.format_exc()}")
            
            self.audit_logger.log_event('vault_unlock_error', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            })
            return False
    
    def lock_vault(self) -> bool:
        """
        Lock the vault and clear all sensitive data from memory
        """
        try:
            self.audit_logger.log_event('vault_lock', {
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Clear session data
            self.session_manager.destroy_session()
            
            # Clear crypto keys from memory
            self.crypto.clear_keys()
            
            # Reset state
            self._is_initialized = False
            self._master_key_hash = None
            
            return True
            
        except Exception as e:
            self.audit_logger.log_event('vault_lock_error', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            })
            return False
    
    def add_image(self, file_path: str, tags: List[str] = None, 
                  metadata: Dict[str, Any] = None) -> Optional[ImageRecord]:
        """
        Add an image to the vault with encryption
        
        Workflow:
        1. Validate file and check for duplicates
        2. Generate unique ID and hash file
        3. Encrypt file with AES-GCM
        4. Create thumbnail
        5. Encrypt metadata and tags
        6. Store everything securely
        """
        if not self._is_initialized:
            raise RuntimeError("Vault not initialized or unlocked")
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Validate file type and size
            if not self.image_processor.validate_image(file_path):
                raise ValueError("Invalid image file")
            
            # Calculate file hash to check for duplicates
            file_hash = self._calculate_file_hash(file_path)
            if self._is_duplicate(file_hash):
                raise ValueError("Duplicate file already exists in vault")
            
            # Generate unique ID
            image_id = str(uuid.uuid4())
            
            # Read original file
            original_size = file_path.stat().st_size
            
            # Encrypt the file
            encrypted_path = self.vault_path / self.config['vault']['data_dir'] / f"{image_id}.enc"
            encrypted_size = self.crypto.encrypt_file(str(file_path), str(encrypted_path))
            
            # Create thumbnail
            thumbnail_path = None
            try:
                thumb_path = self.vault_path / self.config['vault']['thumbnails_dir'] / f"{image_id}_thumb.jpg"
                if self.image_processor.create_thumbnail(str(file_path), str(thumb_path)):
                    thumbnail_path = str(thumb_path)
            except Exception:
                pass  # Thumbnail creation is optional
            
            # Prepare metadata
            full_metadata = {
                'original_filename': file_path.name,
                'file_extension': file_path.suffix,
                'creation_time': datetime.now(timezone.utc).isoformat(),            **(metadata or {})
            }
            
            # Encrypt tags and metadata
            encrypted_tags = self.tag_manager.encrypt_tags(tags or [])
            encrypted_metadata = self.crypto.encrypt_data(json.dumps(full_metadata, ensure_ascii=False).encode('utf-8'))
            
            # Create image record
            image_record = ImageRecord(
                id=image_id,
                name=file_path.name,
                encrypted_path=str(encrypted_path),
                original_size=original_size,
                encrypted_size=encrypted_size,
                mime_type=self.image_processor.get_mime_type(file_path),
                file_hash=file_hash,
                date_added=datetime.now(timezone.utc),
                date_modified=datetime.now(timezone.utc),
                encrypted_tags=encrypted_tags,
                encrypted_metadata=encrypted_metadata,
                thumbnail_path=thumbnail_path
            )
            
            # Store in database (this would be handled by storage layer)
            self._store_image_record(image_record)
            
            self.audit_logger.log_event('image_added', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'image_id': image_id,
                'filename': file_path.name,
                'size': original_size
            })
            
            return image_record
            
        except Exception as e:
            self.audit_logger.log_event('image_add_error', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error': str(e),
                'filename': str(file_path) if 'file_path' in locals() else 'unknown'
            })
            return None
    
    def get_image(self, image_id: str, decrypt: bool = False) -> Optional[bytes]:
        """
        Retrieve an image from the vault
        If decrypt=True, returns decrypted image data
        If decrypt=False, returns encrypted data
        """
        if not self._is_initialized:
            raise RuntimeError("Vault not initialized or unlocked")
        
        try:
            # Get image record
            image_record = self._get_image_record(image_id)
            if not image_record:
                return None
            
            # Read encrypted file
            encrypted_path = Path(image_record.encrypted_path)
            if not encrypted_path.exists():
                return None
            
            if decrypt:
                # Decrypt and return image data
                decrypted_data = self.crypto.decrypt_file_to_memory(str(encrypted_path))
                
                self.audit_logger.log_event('image_accessed', {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'image_id': image_id
                })
                
                return decrypted_data
            else:
                # Return encrypted data
                with open(encrypted_path, 'rb') as f:
                    return f.read()
                    
        except Exception as e:
            self.audit_logger.log_event('image_access_error', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'image_id': image_id,
                'error': str(e)
            })
            return None
    
    def delete_image(self, image_id: str) -> bool:
        """
        Securely delete an image from the vault
        """
        if not self._is_initialized:
            raise RuntimeError("Vault not initialized or unlocked")
        
        try:
            # Get image record
            image_record = self._get_image_record(image_id)
            if not image_record:
                return False
            
            # Securely delete files
            encrypted_path = Path(image_record.encrypted_path)
            if encrypted_path.exists():
                self._secure_delete_file(encrypted_path)
            
            if image_record.thumbnail_path:
                thumb_path = Path(image_record.thumbnail_path)
                if thumb_path.exists():
                    self._secure_delete_file(thumb_path)
            
            # Remove from database
            self._delete_image_record(image_id)
            
            self.audit_logger.log_event('image_deleted', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'image_id': image_id
            })
            
            return True
            
        except Exception as e:
            self.audit_logger.log_event('image_delete_error', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'image_id': image_id,
                'error': str(e)
            })
            return False
    
    def search_images(self, query: str, tag_filters: List[str] = None) -> List[ImageRecord]:
        """
        Search images using encrypted metadata and tags
        """
        if not self._is_initialized:
            raise RuntimeError("Vault not initialized or unlocked")
        
        try:
            # Get all image records
            all_records = self._get_all_image_records()
            
            # Decrypt and search
            results = []
            for record in all_records:
                # Decrypt tags for searching
                decrypted_tags = self.tag_manager.decrypt_tags(record.encrypted_tags)
                
                # Decrypt metadata for searching
                decrypted_metadata = json.loads(
                    self.crypto.decrypt_data(record.encrypted_metadata).decode()
                )
                
                # Apply search logic
                if self.search_engine.matches_query(
                    query, record.name, decrypted_tags, decrypted_metadata, tag_filters
                ):
                    results.append(record)
            
            self.audit_logger.log_event('search_performed', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'query': query,
                'results_count': len(results)
            })
            
            return results
            
        except Exception as e:
            self.audit_logger.log_event('search_error', {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'query': query,
                'error': str(e)
            })
            return []
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-512 hash of file for integrity verification"""
        sha512_hash = hashlib.sha512()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha512_hash.update(chunk)
        return sha512_hash.hexdigest()
    
    def _is_duplicate(self, file_hash: str) -> bool:
        """Check if file hash already exists in vault"""
        # This would query the database for existing hash
        # Placeholder implementation
        return False
    
    def _secure_delete_file(self, file_path: Path) -> None:
        """Securely delete a file by overwriting with random data"""
        if not file_path.exists():
            return
        
        file_size = file_path.stat().st_size
        
        # Overwrite with random data 3 times
        for _ in range(3):
            with open(file_path, 'wb') as f:
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())
        
        # Finally delete the file
        file_path.unlink()
      # Database operations using storage interface
    def _store_image_record(self, record: ImageRecord) -> None:
        """Store image record in database"""
        if self.storage:
            self.storage.store_image(record)
    
    def _get_image_record(self, image_id: str) -> Optional[ImageRecord]:
        """Get image record from database"""
        if self.storage:
            return self.storage.get_image(image_id)
        return None
    
    def _get_all_image_records(self) -> List[ImageRecord]:
        """Get all image records from database"""
        if self.storage:
            return self.storage.get_all_images()
        return []
    
    def _delete_image_record(self, image_id: str) -> None:
        """Delete image record from database"""
        if self.storage:
            self.storage.delete_image(image_id)
    
    def _is_duplicate(self, file_hash: str) -> bool:
        """Check if file hash already exists in vault"""
        if self.storage:
            existing_record = self.storage.get_image_by_hash(file_hash)
            return existing_record is not None
        return False
