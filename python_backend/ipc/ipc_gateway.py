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
            
            if not self.core._is_initialized:
                return {'success': False, 'error': 'Vault not unlocked'}
            
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
            
            # Validate base64 input
            if not file_contents or len(file_contents) < 100:
                return {'success': False, 'error': 'Invalid or empty file contents'}
            
            # Decode the base64 string
            try:
                image_data = base64.b64decode(file_contents)
                print(f"Successfully decoded base64 data: {len(image_data)} bytes", file=sys.stderr)
            except (base64.binascii.Error, TypeError) as e:
                return {'success': False, 'error': f'Invalid base64 data: {e}'}

            # Determine file extension from image data
            file_extension = self._detect_image_format(image_data)
            if not file_extension:
                return {'success': False, 'error': 'Unable to detect image format'}
            
            # Write to a temporary file with proper extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                tmp_file.write(image_data)
                temp_file_path = tmp_file.name
            
            print(f"Created temporary file: {temp_file_path}", file=sys.stderr)

            # Add image through core engine
            image_record = self.core.add_image(temp_file_path, tags or [], metadata or {})
            
            # Clean up the temporary file
            try:
                Path(temp_file_path).unlink()
                print(f"Cleaned up temporary file: {temp_file_path}", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Could not clean up temp file {temp_file_path}: {e}", file=sys.stderr)

            if image_record:
                print(f"Image successfully added with ID: {image_record.id}", file=sys.stderr)
                return {
                    'success': True,
                    'image_id': image_record.id,
                    'message': 'Image added successfully',
                    'data': {
                        'id': image_record.id,
                        'name': image_record.name,
                        'size': image_record.original_size,
                        'mime_type': image_record.mime_type
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to add image to vault'
                }
                
        except Exception as e:
            print(f"Exception in add_image: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'Add image error: {str(e)}'
            }
    
    def _detect_image_format(self, image_data: bytes) -> Optional[str]:
        """Detect image format from binary data"""
        try:
            # Check magic bytes for common image formats
            if image_data.startswith(b'\xff\xd8\xff'):
                return 'jpg'
            elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'png'
            elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
                return 'gif'
            elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
                return 'webp'
            elif image_data.startswith(b'BM'):
                return 'bmp'
            elif image_data.startswith(b'II*\x00') or image_data.startswith(b'MM\x00*'):
                return 'tiff'
            else:
                # Default to jpg if we can't detect
                return 'jpg'
        except Exception:
            return 'jpg'
    
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
    
    # Parse command-line arguments (command and vault-path)
    cli_args, _ = parser.parse_known_args()

    # Read payload from stdin
    payload = {}
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read()
        if stdin_data:
            try:
                payload = json.loads(stdin_data)
            except json.JSONDecodeError as e:
                print(json.dumps({
                    'success': False, 
                    'error': 'Invalid JSON payload from stdin',
                    'details': str(e),
                    'stdin_data': stdin_data
                }), file=sys.stderr)
                sys.exit(1)
    
    try:
        gateway = IPCGateway(cli_args.vault_path)
        
        # Get arguments from payload, with defaults
        password = payload.get('password')
        file_contents = payload.get('file_contents')
        image_id = payload.get('image_id')
        query = payload.get('query')
        tags = payload.get('tags', [])
        metadata = payload.get('metadata', {})
        config = payload.get('config', {})
        decrypt = payload.get('decrypt', False)
        limit = payload.get('limit')
        offset = payload.get('offset', 0)
        
        # Execute command
        result = None
        command = cli_args.command
        
        if command == 'initialize':
            if not password:
                result = {'success': False, 'error': 'Password required'}
            else:
                result = gateway.initialize_vault(password, config)
        
        elif command == 'unlock':
            if not password:
                result = {'success': False, 'error': 'Password required'}
            else:
                result = gateway.unlock_vault(password, config)
        
        elif command == 'lock':
            result = gateway.lock_vault()
        
        elif command == 'get_vault_status':
            result = gateway.get_vault_status()
        
        elif command == 'add_image':
            if not file_contents:
                result = {'success': False, 'error': 'File contents required'}
            else:
                result = gateway.add_image(file_contents, tags, metadata)
        
        elif command == 'get_image':
            if not image_id:
                result = {'success': False, 'error': 'Image ID required'}
            else:
                result = gateway.get_image(image_id, decrypt)
        
        elif command == 'get_all_images':
            result = gateway.get_all_images(limit, offset)
        
        elif command == 'search_images':
            if not query:
                result = {'success': False, 'error': 'Query required'}
            else:
                result = gateway.search_images(query, tags)
        
        elif command == 'delete_image':
            if not image_id:
                result = {'success': False, 'error': 'Image ID required'}
            else:
                result = gateway.delete_image(image_id)
        
        elif command == 'get_stats':
            result = gateway.get_vault_stats()
        
        elif command == 'vault_exists':
            result = gateway.vault_exists()
        
        else:
            result = {'success': False, 'error': f'Unknown command: {command}'}
        
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
