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
    from .core_engine import GraphiVaultCore
    from .storage_interface import StorageInterface
except ImportError:
    from core_engine import GraphiVaultCore
    from storage_interface import StorageInterface


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
            
            if self.core.unlock_vault(master_password):
                # Initialize storage interface
                db_path = self.vault_path / 'database' / 'vault.db'
                self.storage = StorageInterface(str(db_path), self.core.crypto)
                
                return {
                    'success': True,
                    'message': 'Vault unlocked successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to unlock vault - invalid password or vault corrupted'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Unlock error: {str(e)}'
            }
    
    def lock_vault(self) -> Dict[str, Any]:
        """Lock the vault"""
        try:
            if self.core:
                if self.core.lock_vault():
                    return {
                        'success': True,
                        'message': 'Vault locked successfully'
                    }
            
            return {
                'success': False,
                'error': 'Failed to lock vault'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Lock error: {str(e)}'
            }
    
    def add_encrypted_image(self, file_path: str, tags: List[str] = None, 
                           metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add image to vault with encryption"""
        try:
            if not self.core:
                return {'success': False, 'error': 'Vault not initialized'}
            
            image_record = self.core.add_image(file_path, tags or [], metadata or {})
            
            if image_record:
                # Store in database
                if self.storage and self.storage.store_image(image_record):
                    return {
                        'success': True,
                        'data': {
                            'image_id': image_record.id,
                            'message': 'Image added successfully'
                        }
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
    
    def get_decrypted_image(self, image_id: str) -> Dict[str, Any]:
        """Get decrypted image data"""
        try:
            if not self.core:
                return {'success': False, 'error': 'Vault not initialized'}
            
            # Get decrypted image data
            image_data = self.core.get_image(image_id, decrypt=True)
            if image_data:
                # Return base64 encoded data for transport
                import base64
                encoded_data = base64.b64encode(image_data).decode('ascii')
                return {
                    'success': True,
                    'data': {
                        'image_data': encoded_data,
                        'format': 'base64'
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
    
    def get_thumbnail(self, image_id: str) -> Dict[str, Any]:
        """Get image thumbnail"""
        try:
            if not self.core or not self.storage:
                return {'success': False, 'error': 'Vault not initialized'}
            
            # Get image metadata
            image_record = self.storage.get_image(image_id)
            if image_record and image_record.thumbnail_path:
                # Get thumbnail data
                thumbnail_path = self.vault_path / image_record.thumbnail_path
                if thumbnail_path.exists():
                    import base64
                    with open(thumbnail_path, 'rb') as f:
                        thumbnail_data = f.read()
                    encoded_data = base64.b64encode(thumbnail_data).decode('ascii')
                    
                    return {
                        'success': True,
                        'data': {
                            'thumbnail_data': encoded_data,
                            'format': 'base64'
                        }
                    }
            
            return {
                'success': False,
                'error': 'Thumbnail not found'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Get thumbnail error: {str(e)}'
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
                    decrypted_tags = self.core.tag_manager.decrypt_tags(record.encrypted_tags) if self.core else []
                    decrypted_metadata = json.loads(
                        self.core.crypto.decrypt_data(record.encrypted_metadata).decode()
                    ) if self.core else {}
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
                'data': {
                    'images': images,
                    'total_count': len(images)
                }
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
                'data': {
                    'results': formatted_results,
                    'total_results': len(formatted_results)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Search error: {str(e)}'
            }


def main():
    """Main entry point for IPC Gateway"""
    parser = argparse.ArgumentParser(description='GraphiVault IPC Gateway')
    parser.add_argument('--method', required=True, help='Method to execute')
    parser.add_argument('--vault-path', required=True, help='Path to vault directory')
    parser.add_argument('--master_password', help='Master password')
    parser.add_argument('--file_path', help='File path for operations')
    parser.add_argument('--image_id', help='Image ID for operations')
    parser.add_argument('--output_path', help='Output path for operations')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--tags', help='Tags (JSON array as string)')
    parser.add_argument('--metadata', help='Metadata (JSON object as string)')
    parser.add_argument('--config', help='Configuration (JSON object as string)')
    parser.add_argument('--decrypt', action='store_true', help='Decrypt image data')
    parser.add_argument('--limit', type=int, help='Limit for pagination')
    parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    
    args = parser.parse_args()
    
    try:
        gateway = IPCGateway(args.vault_path)
        
        # Parse JSON arguments
        tags = json.loads(args.tags) if args.tags else []
        metadata = json.loads(args.metadata) if args.metadata else {}
        config = json.loads(args.config) if args.config else {}
        
        # Execute method
        result = None
        
        if args.method == 'initialize_vault':
            if not args.master_password:
                result = {'success': False, 'error': 'Master password required'}
            else:
                result = gateway.initialize_vault(args.master_password, config)
        
        elif args.method == 'unlock_vault':
            if not args.master_password:
                result = {'success': False, 'error': 'Master password required'}
            else:
                result = gateway.unlock_vault(args.master_password, config)
        
        elif args.method == 'lock_vault':
            result = gateway.lock_vault()
        
        elif args.method == 'add_encrypted_image':
            if not args.file_path:
                result = {'success': False, 'error': 'File path required'}
            else:
                result = gateway.add_encrypted_image(args.file_path, tags, metadata)
        
        elif args.method == 'get_decrypted_image':
            if not args.image_id:
                result = {'success': False, 'error': 'Image ID required'}
            else:
                result = gateway.get_decrypted_image(args.image_id)
        
        elif args.method == 'get_thumbnail':
            if not args.image_id:
                result = {'success': False, 'error': 'Image ID required'}
            else:
                result = gateway.get_thumbnail(args.image_id)
        
        elif args.method == 'get_all_images':
            result = gateway.get_all_images(args.limit, args.offset)
        
        elif args.method == 'search_images':
            if not args.query:
                result = {'success': False, 'error': 'Search query required'}
            else:
                result = gateway.search_images(args.query, tags)
        
        else:        result = {'success': False, 'error': f'Unknown method: {args.method}'}
        
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
