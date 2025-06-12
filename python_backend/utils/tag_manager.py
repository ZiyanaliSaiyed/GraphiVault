#!/usr/bin/env python3
"""
GraphiVault Tag Manager
Manages encrypted tags and metadata with separate encryption domain
Provides secure tagging system with privacy-first design
"""

import json
from typing import List, Dict, Set, Any, Optional
from datetime import datetime, timezone

try:
    from ..crypto.crypto_controller import CryptoController
except ImportError:
    from crypto.crypto_controller import CryptoController


class TagManager:
    """
    Tag Manager - The keeper of encrypted metadata
    
    Features:
    - Separate encryption domain for tags (tag keychain)
    - Hierarchical tag support (categories)
    - Tag suggestions and auto-completion
    - Secure tag search and filtering
    - Tag analytics and usage statistics
    """
    
    def __init__(self, crypto_controller: CryptoController):
        """Initialize tag manager"""
        self.crypto = crypto_controller
        self._tag_cache = {}  # In-memory cache for performance
        self._tag_stats = {}  # Tag usage statistics
    
    def encrypt_tags(self, tags: List[str]) -> bytes:
        """
        Encrypt a list of tags using the tag keychain
        """
        try:
            # Prepare tag data
            tag_data = {
                'tags': self._normalize_tags(tags),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': '1.0'
            }
            
            # Convert to JSON bytes
            tag_json = json.dumps(tag_data, sort_keys=True).encode('utf-8')
            
            # Encrypt using tag keychain
            encrypted_tags = self.crypto.encrypt_with_tag_keychain(tag_json)
            
            # Update tag statistics
            self._update_tag_stats(tags)
            
            return encrypted_tags
            
        except Exception as e:
            raise RuntimeError(f"Tag encryption failed: {e}")
    
    def decrypt_tags(self, encrypted_tags: bytes) -> List[str]:
        """
        Decrypt tags using the tag keychain
        """
        try:
            # Decrypt tag data
            decrypted_data = self.crypto.decrypt_with_tag_keychain(encrypted_tags)
            
            # Parse JSON
            tag_data = json.loads(decrypted_data.decode('utf-8'))
            
            # Extract tags
            return tag_data.get('tags', [])
            
        except Exception as e:
            raise RuntimeError(f"Tag decryption failed: {e}")
    
    def add_tag(self, existing_encrypted_tags: bytes, new_tag: str) -> bytes:
        """
        Add a new tag to existing encrypted tags
        """
        try:
            # Decrypt existing tags
            existing_tags = self.decrypt_tags(existing_encrypted_tags)
            
            # Add new tag (avoid duplicates)
            normalized_tag = self._normalize_tag(new_tag)
            if normalized_tag not in existing_tags:
                existing_tags.append(normalized_tag)
            
            # Re-encrypt and return
            return self.encrypt_tags(existing_tags)
            
        except Exception as e:
            raise RuntimeError(f"Failed to add tag: {e}")
    
    def remove_tag(self, existing_encrypted_tags: bytes, tag_to_remove: str) -> bytes:
        """
        Remove a tag from existing encrypted tags
        """
        try:
            # Decrypt existing tags
            existing_tags = self.decrypt_tags(existing_encrypted_tags)
            
            # Remove tag
            normalized_tag = self._normalize_tag(tag_to_remove)
            if normalized_tag in existing_tags:
                existing_tags.remove(normalized_tag)
            
            # Re-encrypt and return
            return self.encrypt_tags(existing_tags)
            
        except Exception as e:
            raise RuntimeError(f"Failed to remove tag: {e}")
    
    def update_tags(self, existing_encrypted_tags: bytes, new_tags: List[str]) -> bytes:
        """
        Replace all tags with a new set
        """
        try:
            return self.encrypt_tags(new_tags)
            
        except Exception as e:
            raise RuntimeError(f"Failed to update tags: {e}")
    
    def create_tag_hierarchy(self, tags: List[str]) -> Dict[str, List[str]]:
        """
        Create hierarchical structure from flat tags
        Supports syntax like "category:subcategory" or "category/subcategory"
        """
        hierarchy = {}
        
        try:
            for tag in tags:
                # Check for hierarchy separators
                if ':' in tag:
                    parts = tag.split(':', 1)
                    category, subcategory = parts[0].strip(), parts[1].strip()
                elif '/' in tag:
                    parts = tag.split('/', 1)
                    category, subcategory = parts[0].strip(), parts[1].strip()
                else:
                    # Flat tag
                    category, subcategory = 'general', tag.strip()
                
                if category not in hierarchy:
                    hierarchy[category] = []
                
                if subcategory not in hierarchy[category]:
                    hierarchy[category].append(subcategory)
            
        except Exception:
            # Return flat structure on error
            hierarchy = {'general': tags}
        
        return hierarchy
    
    def suggest_tags(self, partial_tag: str, limit: int = 10) -> List[str]:
        """
        Suggest tags based on partial input and usage statistics
        """
        suggestions = []
        
        try:
            partial_lower = partial_tag.lower().strip()
            
            if not partial_lower:
                # Return most popular tags
                sorted_tags = sorted(
                    self._tag_stats.items(),
                    key=lambda x: x[1].get('count', 0),
                    reverse=True
                )
                return [tag for tag, _ in sorted_tags[:limit]]
            
            # Find matching tags
            matches = []
            for tag, stats in self._tag_stats.items():
                tag_lower = tag.lower()
                
                # Exact prefix match gets highest priority
                if tag_lower.startswith(partial_lower):
                    matches.append((tag, stats.get('count', 0), 0))
                # Contains match gets lower priority
                elif partial_lower in tag_lower:
                    matches.append((tag, stats.get('count', 0), 1))
            
            # Sort by priority, then by usage count
            matches.sort(key=lambda x: (x[2], -x[1]))
            
            suggestions = [tag for tag, _, _ in matches[:limit]]
            
        except Exception:
            pass
        
        return suggestions
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get tag usage statistics
        """
        try:
            total_tags = len(self._tag_stats)
            total_usage = sum(stats.get('count', 0) for stats in self._tag_stats.values())
            
            # Most popular tags
            popular_tags = sorted(
                self._tag_stats.items(),
                key=lambda x: x[1].get('count', 0),
                reverse=True
            )[:10]
            
            # Recent tags
            recent_tags = sorted(
                self._tag_stats.items(),
                key=lambda x: x[1].get('last_used', ''),
                reverse=True
            )[:10]
            
            return {
                'total_unique_tags': total_tags,
                'total_tag_usage': total_usage,
                'most_popular': [{'tag': tag, 'count': stats.get('count', 0)} 
                               for tag, stats in popular_tags],
                'recently_used': [{'tag': tag, 'last_used': stats.get('last_used')} 
                                for tag, stats in recent_tags],
                'average_tags_per_image': total_usage / max(1, total_tags)
            }
            
        except Exception:
            return {
                'total_unique_tags': 0,
                'total_tag_usage': 0,
                'most_popular': [],
                'recently_used': [],
                'average_tags_per_image': 0
            }
    
    def search_by_tags(self, tag_filters: List[str], mode: str = 'all') -> Set[str]:
        """
        Search for images by tags (returns image IDs)
        
        Args:
            tag_filters: List of tags to filter by
            mode: 'all' (AND), 'any' (OR), or 'exact' (exact match)
        """
        # This would require integration with the database/storage layer
        # Placeholder implementation
        matching_images = set()
        
        try:
            # This would query the database for images with matching tags
            # The actual implementation would depend on the storage layer
            pass
            
        except Exception:
            pass
        
        return matching_images
    
    def export_tags(self, format: str = 'json') -> str:
        """
        Export tag statistics and hierarchy
        """
        try:
            export_data = {
                'format': format,
                'exported_at': datetime.now(timezone.utc).isoformat(),
                'version': '1.0',            'statistics': self.get_tag_statistics(),
                'tag_data': self._tag_stats
            }
            
            if format.lower() == 'json':
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            else:
                # Could support other formats like CSV, XML
                return json.dumps(export_data, indent=2, ensure_ascii=False)
                
        except Exception:
            return '{}'
    
    def import_tags(self, import_data: str, format: str = 'json') -> bool:
        """
        Import tag data from export
        """
        try:
            if format.lower() == 'json':
                data = json.loads(import_data)
                
                if 'tag_data' in data:
                    # Merge with existing statistics
                    for tag, stats in data['tag_data'].items():
                        if tag in self._tag_stats:
                            # Merge statistics
                            existing_count = self._tag_stats[tag].get('count', 0)
                            imported_count = stats.get('count', 0)
                            self._tag_stats[tag]['count'] = existing_count + imported_count
                        else:
                            self._tag_stats[tag] = stats
                
                return True
            
        except Exception:
            pass
        
        return False
    
    def _normalize_tag(self, tag: str) -> str:
        """
        Normalize a single tag (trim, lowercase, etc.)
        """
        if not isinstance(tag, str):
            return str(tag).strip().lower()
        
        # Trim whitespace and convert to lowercase
        normalized = tag.strip().lower()
        
        # Remove special characters that might cause issues
        # Keep alphanumeric, hyphens, underscores, and common separators
        allowed_chars = 'abcdefghijklmnopqrstuvwxyz0123456789-_:/.'
        normalized = ''.join(c for c in normalized if c in allowed_chars)
        
        # Remove leading/trailing separators
        normalized = normalized.strip('-_:/')
        
        return normalized
    
    def _normalize_tags(self, tags: List[str]) -> List[str]:
        """
        Normalize a list of tags
        """
        normalized = []
        
        for tag in tags:
            norm_tag = self._normalize_tag(tag)
            if norm_tag and norm_tag not in normalized:
                normalized.append(norm_tag)
        
        return sorted(normalized)  # Sort for consistency
    
    def _update_tag_stats(self, tags: List[str]) -> None:
        """
        Update tag usage statistics
        """
        try:
            current_time = datetime.now(timezone.utc).isoformat()
            
            for tag in self._normalize_tags(tags):
                if tag not in self._tag_stats:
                    self._tag_stats[tag] = {
                        'count': 0,
                        'first_used': current_time,
                        'last_used': current_time
                    }
                
                self._tag_stats[tag]['count'] += 1
                self._tag_stats[tag]['last_used'] = current_time
                
        except Exception:
            pass  # Don't fail the main operation if stats update fails
    
    def clear_cache(self) -> None:
        """
        Clear the in-memory tag cache
        """
        self._tag_cache.clear()
    
    def clear_statistics(self) -> None:
        """
        Clear tag usage statistics
        """
        self._tag_stats.clear()
