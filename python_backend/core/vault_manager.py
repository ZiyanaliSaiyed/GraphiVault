#!/usr/bin/env python3
"""
GraphiVault Vault Manager
Manages vault creation, validation, and structure
Ensures proper vault organization and security policies
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timezone

try:
    from .crypto_controller import CryptoController
except ImportError:
    from crypto_controller import CryptoController


class VaultManager:
    """
    Vault Manager - The architect of secure vault structures
    
    Responsibilities:
    - Create and validate vault directory structure
    - Manage vault metadata and configuration
    - Enforce security policies and access controls
    - Handle vault migration and backup operations
    """
    
    def __init__(self, vault_path: Path, crypto_controller: CryptoController):
        """Initialize vault manager"""
        self.vault_path = vault_path
        self.crypto = crypto_controller
        
        # Vault directory structure
        self.directories = {
            'data': vault_path / 'data',           # Encrypted image files
            'thumbnails': vault_path / 'thumbnails', # Encrypted thumbnails
            'temp': vault_path / 'temp',           # Temporary files
            'metadata': vault_path / 'metadata',   # Vault metadata
            'backups': vault_path / 'backups'      # Backup files
        }
        
        self.vault_config_path = vault_path / 'vault.config'
        self.vault_key_path = vault_path / 'vault.key'
    
    def create_vault(self) -> bool:
        """
        Create a new vault with proper directory structure
        """
        try:
            # Create vault root directory
            self.vault_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            for dir_name, dir_path in self.directories.items():
                dir_path.mkdir(exist_ok=True)
                
                # Create .gitkeep files to preserve directory structure
                gitkeep = dir_path / '.gitkeep'
                gitkeep.touch()
            
            # Create vault configuration
            vault_config = {
                'vault_id': str(uuid.uuid4()),
                'version': '1.0.0',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'encrypted': True,
                'compression_enabled': False,
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
                'security_level': 'high',
                'backup_enabled': True,
                'audit_logging': True
            }
            
            # Write configuration
            with open(self.vault_config_path, 'w') as f:
                json.dump(vault_config, f, indent=2)
            
            # Create vault key file (encrypted master key storage)
            self._create_vault_key_file()
            
            return True
            
        except Exception:
            # Clean up on failure
            if self.vault_path.exists():
                self._cleanup_vault()
            return False
    
    def vault_exists(self) -> bool:
        """Check if a valid vault exists at the specified path"""
        try:
            # Check if vault directory exists
            if not self.vault_path.exists():
                return False
            
            # Check if configuration file exists
            if not self.vault_config_path.exists():
                return False
            
            # Check if key file exists
            if not self.vault_key_path.exists():
                return False
            
            # Validate directory structure
            for dir_path in self.directories.values():
                if not dir_path.exists():
                    return False
            
            # Validate configuration file
            config = self.get_vault_config()
            if not config or 'vault_id' not in config:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_vault_config(self) -> Optional[Dict[str, Any]]:
        """Get vault configuration"""
        try:
            if not self.vault_config_path.exists():
                return None
            
            with open(self.vault_config_path, 'r') as f:
                return json.load(f)
                
        except Exception:
            return None
    
    def update_vault_config(self, config: Dict[str, Any]) -> bool:
        """Update vault configuration"""
        try:
            # Merge with existing config
            existing_config = self.get_vault_config() or {}
            existing_config.update(config)
            existing_config['modified_at'] = datetime.now(timezone.utc).isoformat()
            
            # Write updated configuration
            with open(self.vault_config_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def get_vault_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        try:
            stats = {
                'total_images': 0,
                'total_size': 0,
                'encrypted_size': 0,
                'thumbnails_count': 0,
                'last_accessed': None,
                'vault_health': 'unknown'
            }
            
            # Count files in data directory
            data_dir = self.directories['data']
            if data_dir.exists():
                data_files = list(data_dir.glob('*.enc'))
                stats['total_images'] = len(data_files)
                stats['encrypted_size'] = sum(f.stat().st_size for f in data_files)
            
            # Count thumbnails
            thumb_dir = self.directories['thumbnails']
            if thumb_dir.exists():
                thumb_files = list(thumb_dir.glob('*_thumb.jpg'))
                stats['thumbnails_count'] = len(thumb_files)
            
            # Vault health check
            stats['vault_health'] = self._check_vault_health()
            
            return stats
            
        except Exception:
            return {'vault_health': 'error'}
    
    def cleanup_temp_files(self) -> bool:
        """Clean up temporary files"""
        try:
            temp_dir = self.directories['temp']
            if not temp_dir.exists():
                return True
            
            # Remove all files in temp directory
            for temp_file in temp_dir.iterdir():
                if temp_file.is_file():
                    temp_file.unlink()
            
            return True
            
        except Exception:
            return False
    
    def create_backup(self, backup_path: str) -> bool:
        """Create a backup of the vault"""
        try:
            backup_path = Path(backup_path)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Create backup metadata
            backup_metadata = {
                'backup_id': str(uuid.uuid4()),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'vault_path': str(self.vault_path),
                'vault_config': self.get_vault_config()
            }
            
            # Copy vault files (implementation would depend on requirements)
            # This is a placeholder for the actual backup logic
            
            # Save backup metadata
            backup_metadata_path = backup_path / 'backup_metadata.json'
            with open(backup_metadata_path, 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def validate_vault_integrity(self) -> Dict[str, Any]:
        """Validate vault integrity and structure"""
        try:
            integrity_report = {
                'valid': True,
                'issues': [],
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Check directory structure
            for dir_name, dir_path in self.directories.items():
                if not dir_path.exists():
                    integrity_report['valid'] = False
                    integrity_report['issues'].append(f"Missing directory: {dir_name}")
            
            # Check configuration file
            config = self.get_vault_config()
            if not config:
                integrity_report['valid'] = False
                integrity_report['issues'].append("Missing or invalid vault configuration")
            
            # Check key file
            if not self.vault_key_path.exists():
                integrity_report['valid'] = False
                integrity_report['issues'].append("Missing vault key file")
            
            # Check for orphaned files
            orphaned_files = self._find_orphaned_files()
            if orphaned_files:
                integrity_report['issues'].extend([
                    f"Orphaned file: {f}" for f in orphaned_files
                ])
            
            return integrity_report
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"Integrity check failed: {str(e)}"],
                'checked_at': datetime.now(timezone.utc).isoformat()
            }
    
    def _create_vault_key_file(self) -> bool:
        """Create encrypted vault key file"""
        try:
            # This would store encrypted master key derivation parameters
            # For now, just create a placeholder
            key_data = {
                'version': '1.0',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'key_algorithm': 'PBKDF2-HMAC-SHA512',
                'iterations': 200000
            }
            
            with open(self.vault_key_path, 'w') as f:
                json.dump(key_data, f)
            
            return True
            
        except Exception:
            return False
    
    def _check_vault_health(self) -> str:
        """Check overall vault health"""
        try:
            # Basic health checks
            if not self.vault_exists():
                return 'corrupted'
            
            # Check if directories are accessible
            for dir_path in self.directories.values():
                if not dir_path.exists() or not os.access(dir_path, os.R_OK | os.W_OK):
                    return 'degraded'
            
            # Check configuration validity
            config = self.get_vault_config()
            if not config or 'vault_id' not in config:
                return 'degraded'
            
            return 'healthy'
            
        except Exception:
            return 'error'
    
    def _find_orphaned_files(self) -> list:
        """Find files that don't belong to any known image record"""
        orphaned = []
        
        try:
            # Check data directory for unknown .enc files
            data_dir = self.directories['data']
            if data_dir.exists():
                for file_path in data_dir.iterdir():
                    if file_path.is_file() and file_path.suffix == '.enc':
                        # Check if this file is referenced in database
                        # This would require database integration
                        pass
            
            # Check thumbnails directory for orphaned thumbnails
            thumb_dir = self.directories['thumbnails']
            if thumb_dir.exists():
                for file_path in thumb_dir.iterdir():
                    if file_path.is_file() and file_path.name.endswith('_thumb.jpg'):
                        # Check if corresponding image exists
                        pass
            
        except Exception:
            pass
        
        return orphaned
    
    def _cleanup_vault(self) -> None:
        """Clean up vault directory on creation failure"""
        try:
            if self.vault_path.exists():
                # Remove all created files and directories
                for item in self.vault_path.rglob('*'):
                    if item.is_file():
                        item.unlink()
                
                # Remove directories (bottom-up)
                for item in sorted(self.vault_path.rglob('*'), reverse=True):
                    if item.is_dir():
                        item.rmdir()
                
                # Remove vault root if empty
                if not any(self.vault_path.iterdir()):
                    self.vault_path.rmdir()
                    
        except Exception:
            pass  # Best effort cleanup
