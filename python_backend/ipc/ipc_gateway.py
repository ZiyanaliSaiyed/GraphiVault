#!/usr/bin/env python3
"""
GraphiVault IPC Gateway
Secure bridge between Tauri frontend and Python backend
Exposes select methods through command-line interface for Tauri integration
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
import traceback

try:
    from ..core.core_engine import GraphiVaultCore
    from ..storage.storage_interface import StorageInterface
except ImportError:
    from core.core_engine import GraphiVaultCore
    from storage.storage_interface import StorageInterface


class IPCGateway:
    """
    IPC Gateway - The secure bridge to the frontend
    
    Features:
    - Command-line interface for Tauri integration
    - Secure method exposure with validation
    - Error handling and sanitization
    - Session management integration
    - Audit logging for all operations
    """
    
    def __init__(self, vault_path: str):
        """Initialize IPC Gateway"""
        self.vault_path = Path(vault_path)
        self.core = None
        self.storage = None
        
    def initialize_vault(self, master_password: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Initialize vault with master password"""
        try:
            self.core = GraphiVaultCore(str(self.vault_path), config)
            
            if self.core.initialize_vault(master_password):
                # Initialize storage interface
                db_path = self.vault_path / 'database' / 'vault.db'
                self.storage = StorageInterface(str(db_path), self.core.crypto)
                
                return {
                    'success': True,
                    'message': 'Vault initialized successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initialize vault'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Initialization error: {str(e)}'
            }
    
    def unlock_vault(self, master_password: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Unlock existing vault"""
        try:
            self.core = GraphiVaultCore(str(self.vault_path), config)
            # Check if vault directory and files exist
            vault_config = self.vault_path / 'vault.config'
            vault_key = self.vault_path / 'vault.key'
            db_path = self.vault_path / 'database' / 'vault.db'
            missing = []
            if not self.vault_path.exists():
                missing.append(str(self.vault_path))
            if not vault_config.exists():
                missing.append(str(vault_config))
            if not vault_key.exists():
                missing.append(str(vault_key))
            if not db_path.exists():
                missing.append(str(db_path))
            if missing:
                return {
                    'success': False,
                    'error': f'Missing vault files: {", ".join(missing)}',
                    'details': {
                        'missing_files': missing
                    }
                }
            # Try to unlock
            unlock_result = self.core.unlock_vault(master_password)
            if unlock_result is True:
                self.storage = StorageInterface(str(db_path), self.core.crypto)
                return {
                    'success': True,
                    'message': 'Vault unlocked successfully'
                }
            else:
                # Check if password is likely wrong or vault is corrupted
                # (core_engine unlock_vault returns False for both)
                # Try to distinguish by checking if the vault is valid
                if hasattr(self.core, 'vault_manager') and hasattr(self.core.vault_manager, 'vault_exists'):
                    if not self.core.vault_manager.vault_exists():
                        return {
                            'success': False,
                            'error': 'Vault structure is corrupted or incomplete',
                            'details': {
                                'reason': 'vault_structure',
                                'vault_path': str(self.vault_path)
                            }
                        }
                return {
                    'success': False,
                    'error': 'Failed to unlock vault: invalid password or vault corrupted',
                    'details': {
                        'reason': 'invalid_password_or_corrupt',
                        'vault_path': str(self.vault_path)
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unlock error: {str(e)}',
                'traceback': traceback.format_exc()
            }
    
    def lock_vault(self) -> Dict[str, Any]:
        """Lock the vault"""
        try:
            # If core is not initialized, the vault is already locked
            if not self.core:
                return {
                    'success': True,
                    'message': 'Vault is already locked'
                }
            
            # Try to lock the vault
            if self.core.lock_vault():
                # Clear the core and storage references
                self.core = None
                self.storage = None
                return {
                    'success': True,
                    'message': 'Vault locked successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to lock vault core'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Lock error: {str(e)}'
            }
    
    def get_vault_status(self) -> Dict[str, Any]:
        """Get vault status and information"""
        try:
            # Check if vault exists without initializing core
            vault_path = Path(str(self.vault_path))
            
            # Basic directory structure check
            vault_exists = (
                vault_path.exists() and
                (vault_path / 'vault.config').exists() and
                (vault_path / 'vault.key').exists() and
                (vault_path / 'database').exists()
            )
            
            if not vault_exists:
                return {
                    'success': True,
                    'vault_exists': False,
                    'is_locked': True,
                    'message': 'No vault found at this location'
                }
            
            # If we have an initialized core, check if it's unlocked
            is_unlocked = (
                self.core is not None and 
                hasattr(self.core, '_is_initialized') and 
                self.core._is_initialized
            )
            
            return {
                'success': True,
                'vault_exists': True,
                'is_locked': not is_unlocked,
                'vault_path': str(self.vault_path),
                'message': 'Vault locked' if not is_unlocked else 'Vault unlocked'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Status check error: {str(e)}'
            }
    
    def add_image(self, file_contents: str, tags: List[str] = None, 
                  metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add image to vault from base64 encoded string"""
        try:
            if not self.core:
                return {'success': False, 'error': 'Vault not initialized'}
            
            import base64
            import tempfile
            
            # Log received parameters
            print(f"Received add_image call with tags: {tags}, type: {type(tags)}", file=sys.stderr)
            
            # Ensure tags is a list
            if tags is None:
                tags = []
            elif not isinstance(tags, list):
                print(f"Tags is not a list: {tags}, attempting to convert", file=sys.stderr)
                try:
                    # Try to convert tags to a list if it's a string
                    if isinstance(tags, str):
                        tags = json.loads(tags)
                    else:
                        tags = list(tags)
                except Exception as e:
                    print(f"Could not convert tags to list: {e}", file=sys.stderr)
                    tags = []
            
            # Decode the base64 string
            try:
                image_data = base64.b64decode(file_contents)
            except (base64.binascii.Error, TypeError) as e:
                return {'success': False, 'error': f'Invalid base64 data: {e}'}

            # Write to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
                tmp_file.write(image_data)
                temp_file_path = tmp_file.name

            image_record = self.core.add_image(temp_file_path, tags or [], metadata or {})
            
            # Clean up the temporary file
            Path(temp_file_path).unlink()

            if image_record:
                # Store in database
                if self.storage and self.storage.store_image(image_record):
                    return {
                        'success': True,
                        'image_id': image_record.id,
                        'message': 'Image added successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to store image in database'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Failed to add image to vault'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Add image error: {str(e)}'
            }
    
    def get_image(self, image_id: str, decrypt: bool = False) -> Dict[str, Any]:
        """Get image from vault"""
        try:
            if not self.core:
                return {'success': False, 'error': 'Vault not initialized'}
            
            if decrypt:
                # Get decrypted image data
                image_data = self.core.get_image(image_id, decrypt=True)
                if image_data:
                    # Return base64 encoded data for transport
                    import base64
                    encoded_data = base64.b64encode(image_data).decode('ascii')
                    return {
                        'success': True,
                        'image_data': encoded_data
                    }
            else:
                # Get image metadata only
                if self.storage:
                    image_record = self.storage.get_image(image_id)
                    if image_record:
                        return {
                            'success': True,
                            'image_record': {
                                'id': image_record.id,
                                'name': image_record.name,
                                'size': image_record.original_size,
                                'mime_type': image_record.mime_type,
                                'date_added': image_record.date_added.isoformat(),
                                'date_modified': image_record.date_modified.isoformat(),
                                'thumbnail_path': image_record.thumbnail_path,
                                'is_encrypted': image_record.is_encrypted
                            }
                        }
            
            return {
                'success': False,
                'error': 'Image not found'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Get image error: {str(e)}'
            }
    
    def get_all_images(self, limit: int = None, offset: int = 0) -> Dict[str, Any]:
        """Get all images from vault"""
        try:
            if not self.storage:
                return {'success': False, 'error': 'Storage not initialized'}
            
            image_records = self.storage.get_all_images(limit, offset)
            
            images = []
            for record in image_records:
                # Decrypt tags and metadata for display
                try:
                    decrypted_tags = self.core.tag_manager.decrypt_tags(record.encrypted_tags)
                    decrypted_metadata = json.loads(
                        self.core.crypto.decrypt_data(record.encrypted_metadata).decode()
                    )
                except Exception:
                    decrypted_tags = []
                    decrypted_metadata = {}
                
                images.append({
                    'id': record.id,
                    'name': record.name,
                    'size': record.original_size,
                    'mime_type': record.mime_type,
                    'date_added': record.date_added.isoformat(),
                    'date_modified': record.date_modified.isoformat(),
                    'tags': decrypted_tags,
                    'metadata': decrypted_metadata,
                    'thumbnail_path': record.thumbnail_path,
                    'is_encrypted': record.is_encrypted
                })
            
            return {
                'success': True,
                'images': images,
                'total_count': len(images)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Get images error: {str(e)}'
            }
    
    def search_images(self, query: str, tag_filters: List[str] = None) -> Dict[str, Any]:
        """Search images in vault"""
        try:
            if not self.core or not self.storage:
                return {'success': False, 'error': 'Vault not initialized'}
            
            # Log received parameters
            print(f"Received search_images call with query: {query}, tag_filters: {tag_filters}, type: {type(tag_filters)}", file=sys.stderr)
            
            # Ensure tag_filters is a list
            if tag_filters is None:
                tag_filters = []
            elif not isinstance(tag_filters, list):
                print(f"tag_filters is not a list: {tag_filters}, attempting to convert", file=sys.stderr)
                try:
                    # Try to convert tag_filters to a list if it's a string
                    if isinstance(tag_filters, str):
                        tag_filters = json.loads(tag_filters)
                    else:
                        tag_filters = list(tag_filters)
                except Exception as e:
                    print(f"Could not convert tag_filters to list: {e}", file=sys.stderr)
                    tag_filters = []
            
            # Get all images for searching (in a real implementation, this would be optimized)
            all_records = self.storage.get_all_images()
            
            # Convert to searchable format
            searchable_records = []
            for record in all_records:
                try:
                    decrypted_tags = self.core.tag_manager.decrypt_tags(record.encrypted_tags)
                    decrypted_metadata = json.loads(
                        self.core.crypto.decrypt_data(record.encrypted_metadata).decode()
                    )
                    
                    searchable_records.append({
                        'id': record.id,
                        'name': record.name,
                        'tags': decrypted_tags,
                        'metadata': decrypted_metadata,
                        'size': record.original_size,
                        'mimeType': record.mime_type,
                        'dateAdded': record.date_added.isoformat()
                    })
                except Exception:
                    continue
            
            # Perform search
            results = self.core.search_engine.search_and_rank(
                query, searchable_records, tag_filters
            )
            
            # Format results
            formatted_results = []
            for record_data, score in results:
                formatted_results.append({
                    'id': record_data['id'],
                    'name': record_data['name'],
                    'tags': record_data['tags'],
                    'metadata': record_data['metadata'],
                    'size': record_data['size'],
                    'mime_type': record_data['mimeType'],
                    'date_added': record_data['dateAdded'],
                    'relevance_score': score
                })
            
            return {
                'success': True,
                'results': formatted_results,
                'total_results': len(formatted_results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Search error: {str(e)}'
            }
    
    def delete_image(self, image_id: str) -> Dict[str, Any]:
        """Delete image from vault"""
        try:
            if not self.core or not self.storage:
                return {'success': False, 'error': 'Vault not initialized'}
            
            # Delete from core engine (handles file deletion)
            if self.core.delete_image(image_id):
                # Delete from database
                if self.storage.delete_image(image_id):
                    return {
                        'success': True,
                        'message': 'Image deleted successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to delete from database'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Failed to delete image files'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Delete error: {str(e)}'
            }
    
    def get_vault_stats(self) -> Dict[str, Any]:
        """Get vault statistics"""
        try:
            if not self.storage:
                return {'success': False, 'error': 'Storage not initialized'}
            
            storage_stats = self.storage.get_storage_stats()
            
            # Add additional stats from core components
            stats = {
                'success': True,
                'statistics': {
                    **storage_stats,
                    'vault_path': str(self.vault_path),
                    'is_locked': not (self.core and self.core._is_initialized)
                }
            }
            
            if self.core:
                # Add tag statistics
                tag_stats = self.core.tag_manager.get_tag_statistics()
                stats['statistics']['tag_statistics'] = tag_stats
                
                # Add session information
                session_info = self.core.session_manager.get_session_info()
                stats['statistics']['session_info'] = session_info
            
            return stats
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Stats error: {str(e)}'
            }
    
    def encrypt_file(self, file_path: str, password: str) -> Dict[str, Any]:
        """Encrypt a file (legacy interface for compatibility)"""
        try:
            if not self.core:
                return {'success': False, 'error': 'Vault not initialized'}
            
            input_path = Path(file_path)
            if not input_path.exists():
                return {'success': False, 'error': 'File not found'}
            
            # Generate output path
            output_path = input_path.with_suffix(input_path.suffix + '.encrypted')
            
            # Encrypt file
            encrypted_size = self.core.crypto.encrypt_file(str(input_path), str(output_path))
            
            return {
                'success': True,
                'encrypted_path': str(output_path),
                'encrypted_size': encrypted_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Encryption error: {str(e)}'
            }
    
    def decrypt_file(self, encrypted_path: str, password: str, output_path: str) -> Dict[str, Any]:
        """Decrypt a file (legacy interface for compatibility)"""
        try:
            if not self.core:
                return {'success': False, 'error': 'Vault not initialized'}
            
            if self.core.crypto.decrypt_file(encrypted_path, output_path):
                return {
                    'success': True,
                    'decrypted_path': output_path
                }
            else:
                return {
                    'success': False,
                    'error': 'Decryption failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Decryption error: {str(e)}'
            }

    def vault_exists(self) -> Dict[str, Any]:
        """Check if the vault exists at the specified path."""
        try:
            vault_path = Path(self.vault_path)
            
            # Check for essential vault components
            config_exists = (vault_path / 'vault.config').exists()
            key_exists = (vault_path / 'vault.key').exists()
            db_dir_exists = (vault_path / 'database').exists()

            exists = vault_path.is_dir() and config_exists and key_exists and db_dir_exists
            
            return {
                'success': True,
                'data': {
                    'exists': exists
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error checking vault existence: {str(e)}',
                'traceback': traceback.format_exc()
            }


def main():
    """Main entry point for IPC Gateway"""
    # Fix for UnicodeEncodeError on Windows when printing JSON with emojis
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description='GraphiVault IPC Gateway')
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('--vault-path', required=True, help='Path to vault directory')
    parser.add_argument('--password', help='Master password')
    parser.add_argument('--file-contents', help='File contents for operations (base64 encoded)')
    parser.add_argument('--image-id', help='Image ID for operations')
    parser.add_argument('--output-path', help='Output path for operations')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--tags', help='Tags (JSON array)')
    parser.add_argument('--metadata', help='Metadata (JSON object)')
    parser.add_argument('--config', help='Configuration (JSON object)')
    parser.add_argument('--decrypt', action='store_true', help='Decrypt image data')
    parser.add_argument('--limit', type=int, help='Limit for pagination')
    parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    
    args = parser.parse_args()
    
    try:
        gateway = IPCGateway(args.vault_path)
        
        # Enhanced debugging for received arguments
        print(f"Command: {args.command}", file=sys.stderr)
        print(f"Vault path: {args.vault_path}", file=sys.stderr)
        if args.tags:
            print(f"Raw tags value: {args.tags!r}", file=sys.stderr)
        if args.metadata:
            print(f"Raw metadata value: {args.metadata!r}", file=sys.stderr)
        
        # Parse JSON arguments with enhanced error handling
        try:
            tags = json.loads(args.tags) if args.tags else []
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing tags: {e}, raw value: {args.tags!r}", file=sys.stderr)
            tags = []
            
        try:
            metadata = json.loads(args.metadata) if args.metadata else {}
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing metadata: {e}, raw value: {args.metadata!r}", file=sys.stderr)
            metadata = {}
            
        try:
            config = json.loads(args.config) if args.config else {}
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing config: {e}, raw value: {args.config!r}", file=sys.stderr)
            config = {}
        
        # Execute command
        result = None
        
        if args.command == 'initialize':
            if not args.password:
                result = {'success': False, 'error': 'Password required'}
            else:
                result = gateway.initialize_vault(args.password, config)
        
        elif args.command == 'unlock':
            if not args.password:
                result = {'success': False, 'error': 'Password required'}
            else:
                result = gateway.unlock_vault(args.password, config)
        
        elif args.command == 'lock':
            result = gateway.lock_vault()
        
        elif args.command == 'get_vault_status':
            result = gateway.get_vault_status()
        
        elif args.command == 'add_image':
            if not args.file_contents:
                result = {'success': False, 'error': 'File contents required'}
            else:
                result = gateway.add_image(args.file_contents, tags, metadata)
        
        elif args.command == 'get_image':
            if not args.image_id:
                result = {'success': False, 'error': 'Image ID required'}
            else:
                result = gateway.get_image(args.image_id, args.decrypt)
        
        elif args.command == 'get_all_images':
            result = gateway.get_all_images(args.limit, args.offset)
        
        elif args.command == 'search_images':
            if not args.query:
                result = {'success': False, 'error': 'Query required'}
            else:
                tag_filters = json.loads(args.tags) if args.tags else []
                result = gateway.search_images(args.query, tag_filters)
        
        elif args.command == 'delete_image':
            if not args.image_id:
                result = {'success': False, 'error': 'Image ID required'}
            else:
                result = gateway.delete_image(args.image_id)
        
        elif args.command == 'get_stats':
            result = gateway.get_vault_stats()
        
        elif args.command == 'get_vault_status':
            result = gateway.get_vault_status()
        
        elif args.command == 'encrypt_file':
            if not args.file_path or not args.password:
                result = {'success': False, 'error': 'File path and password required'}
            else:
                result = gateway.encrypt_file(args.file_path, args.password)
        
        elif args.command == 'decrypt_file':
            if not args.file_path or not args.password or not args.output_path:
                result = {'success': False, 'error': 'File path, password, and output path required'}
            else:
                result = gateway.decrypt_file(args.file_path, args.password, args.output_path)
        else:
            result = {'success': False, 'error': f'Unknown command: {args.command}'}
        
        # Output result as JSON with UTF-8 compliance
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Exit with appropriate code
        sys.exit(0 if result.get('success', False) else 1)
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': f'Gateway error: {str(e)}',
            'traceback': traceback.format_exc()
        }
        print(json.dumps(error_result, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == '__main__':
    main()
