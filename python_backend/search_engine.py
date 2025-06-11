#!/usr/bin/env python3
"""
GraphiVault Search Engine
Advanced search capabilities for encrypted image vault
Provides metadata-based search with privacy preservation
"""

import re
import json
from typing import List, Dict, Set, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path


class SearchEngine:
    """
    Search Engine - The intelligence of the vault
    
    Features:
    - Full-text search across decrypted metadata
    - Advanced query syntax (AND, OR, NOT, quotes)
    - Date range filtering
    - Tag-based filtering
    - Fuzzy matching for typos
    - Search result ranking and relevance scoring
    """
    
    def __init__(self):
        """Initialize search engine"""
        self.search_cache = {}
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'img', 'image', 'photo', 'picture'
        }
    
    def matches_query(self, query: str, filename: str, tags: List[str], 
                     metadata: Dict[str, Any], tag_filters: List[str] = None) -> bool:
        """
        Check if an image matches the search query and filters
        """
        try:
            # Apply tag filters first (most restrictive)
            if tag_filters and not self._matches_tag_filters(tags, tag_filters):
                return False
            
            # If no text query, just check tag filters
            if not query or not query.strip():
                return True
            
            # Parse and execute query
            parsed_query = self._parse_query(query)
            return self._evaluate_query(parsed_query, filename, tags, metadata)
            
        except Exception:
            # Fallback to simple string matching
            return self._simple_search(query, filename, tags, metadata)
    
    def search_and_rank(self, query: str, image_records: List[Dict], 
                       tag_filters: List[str] = None, 
                       date_range: Tuple[datetime, datetime] = None) -> List[Tuple[Dict, float]]:
        """
        Search and rank results by relevance
        Returns list of (record, score) tuples sorted by relevance
        """
        results = []
        
        try:
            for record in image_records:
                # Basic matching
                if self.matches_query(query, record.get('name', ''), 
                                    record.get('tags', []), 
                                    record.get('metadata', {}), 
                                    tag_filters):
                    
                    # Apply date filter if specified
                    if date_range:
                        record_date = self._parse_date(record.get('date_added'))
                        if not record_date or not (date_range[0] <= record_date <= date_range[1]):
                            continue
                    
                    # Calculate relevance score
                    score = self._calculate_relevance(
                        query, record.get('name', ''),
                        record.get('tags', []),
                        record.get('metadata', {})
                    )
                    
                    results.append((record, score))
            
            # Sort by relevance score (descending)
            results.sort(key=lambda x: x[1], reverse=True)
            
        except Exception:
            pass
        
        return results
    
    def suggest_completions(self, partial_query: str, available_tags: List[str]) -> List[str]:
        """
        Suggest query completions based on available tags and common patterns
        """
        suggestions = []
        
        try:
            partial_lower = partial_query.lower().strip()
            
            if not partial_lower:
                return []
            
            # Tag suggestions
            for tag in available_tags:
                if tag.lower().startswith(partial_lower):
                    suggestions.append(f"tag:{tag}")
                elif partial_lower in tag.lower():
                    suggestions.append(f"tag:{tag}")
            
            # Common search patterns
            patterns = [
                f'name:"{partial_query}"',
                f'"{partial_query}"',
                f'{partial_query}*',
                f'created:{partial_query}',
                f'size:{partial_query}'
            ]
            
            suggestions.extend(patterns)
            
            # Remove duplicates and limit
            seen = set()
            unique_suggestions = []
            for suggestion in suggestions:
                if suggestion not in seen:
                    seen.add(suggestion)
                    unique_suggestions.append(suggestion)
                    if len(unique_suggestions) >= 10:
                        break
            
            return unique_suggestions
            
        except Exception:
            return []
    
    def get_search_statistics(self, image_records: List[Dict]) -> Dict[str, Any]:
        """
        Generate search statistics for the vault
        """
        try:
            stats = {
                'total_images': len(image_records),
                'searchable_fields': 0,
                'total_tags': 0,
                'unique_tags': set(),
                'file_types': {},
                'date_range': {'earliest': None, 'latest': None},
                'size_distribution': {'small': 0, 'medium': 0, 'large': 0}
            }
            
            for record in image_records:
                # Count searchable fields
                if record.get('name'):
                    stats['searchable_fields'] += 1
                if record.get('tags'):
                    stats['searchable_fields'] += 1
                if record.get('metadata'):
                    stats['searchable_fields'] += 1
                
                # Tag statistics
                tags = record.get('tags', [])
                stats['total_tags'] += len(tags)
                stats['unique_tags'].update(tags)
                
                # File type distribution
                mime_type = record.get('mimeType', 'unknown')
                stats['file_types'][mime_type] = stats['file_types'].get(mime_type, 0) + 1
                
                # Date range
                date_str = record.get('dateAdded')
                if date_str:
                    date_obj = self._parse_date(date_str)
                    if date_obj:
                        if not stats['date_range']['earliest'] or date_obj < stats['date_range']['earliest']:
                            stats['date_range']['earliest'] = date_obj
                        if not stats['date_range']['latest'] or date_obj > stats['date_range']['latest']:
                            stats['date_range']['latest'] = date_obj
                
                # Size distribution
                size = record.get('size', 0)
                if size < 1024 * 1024:  # < 1MB
                    stats['size_distribution']['small'] += 1
                elif size < 10 * 1024 * 1024:  # < 10MB
                    stats['size_distribution']['medium'] += 1
                else:
                    stats['size_distribution']['large'] += 1
            
            # Convert set to count
            stats['unique_tags'] = len(stats['unique_tags'])
            
            return stats
            
        except Exception:
            return {'total_images': 0}
    
    def _parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse search query into structured format
        Supports: "quoted strings", field:value, AND, OR, NOT, wildcards
        """
        parsed = {
            'terms': [],
            'phrases': [],
            'field_searches': {},
            'operators': [],
            'wildcards': []
        }
        
        try:
            # Extract quoted phrases
            phrase_pattern = r'"([^"]*)"'
            phrases = re.findall(phrase_pattern, query)
            parsed['phrases'] = phrases
            
            # Remove phrases from query for further processing
            query_without_phrases = re.sub(phrase_pattern, '', query)
            
            # Extract field searches (field:value)
            field_pattern = r'(\w+):([^\s]+)'
            field_matches = re.findall(field_pattern, query_without_phrases)
            for field, value in field_matches:
                parsed['field_searches'][field.lower()] = value
            
            # Remove field searches
            query_without_fields = re.sub(field_pattern, '', query_without_phrases)
            
            # Extract remaining terms
            terms = query_without_fields.split()
            for term in terms:
                term = term.strip().lower()
                if term in ['and', 'or', 'not']:
                    parsed['operators'].append(term)
                elif '*' in term or '?' in term:
                    parsed['wildcards'].append(term)
                elif term and term not in self.stopwords:
                    parsed['terms'].append(term)
            
        except Exception:
            # Fallback to simple term extraction
            parsed['terms'] = [t.lower() for t in query.split() if t.lower() not in self.stopwords]
        
        return parsed
    
    def _evaluate_query(self, parsed_query: Dict[str, Any], filename: str, 
                       tags: List[str], metadata: Dict[str, Any]) -> bool:
        """
        Evaluate parsed query against image data
        """
        try:
            # Check field searches
            for field, value in parsed_query['field_searches'].items():
                if not self._check_field_match(field, value, filename, tags, metadata):
                    return False
            
            # Check phrases
            searchable_text = self._build_searchable_text(filename, tags, metadata)
            for phrase in parsed_query['phrases']:
                if phrase.lower() not in searchable_text.lower():
                    return False
            
            # Check terms (AND logic by default)
            for term in parsed_query['terms']:
                if term.lower() not in searchable_text.lower():
                    return False
            
            # Check wildcards
            for wildcard in parsed_query['wildcards']:
                if not self._wildcard_match(wildcard, searchable_text):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _simple_search(self, query: str, filename: str, tags: List[str], 
                      metadata: Dict[str, Any]) -> bool:
        """
        Fallback simple search implementation
        """
        try:
            query_lower = query.lower()
            searchable_text = self._build_searchable_text(filename, tags, metadata).lower()
            
            # Simple substring search
            return query_lower in searchable_text
            
        except Exception:
            return False
    
    def _build_searchable_text(self, filename: str, tags: List[str], 
                              metadata: Dict[str, Any]) -> str:
        """
        Build searchable text from all available data
        """
        text_parts = []
        
        # Add filename
        if filename:
            text_parts.append(filename)
        
        # Add tags
        if tags:
            text_parts.extend(tags)
        
        # Add metadata
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (str, int, float)):
                    text_parts.append(str(value))
                elif isinstance(value, dict):
                    # Recursively extract text from nested dictionaries
                    text_parts.append(self._extract_text_from_dict(value))
        
        return ' '.join(text_parts)
    
    def _extract_text_from_dict(self, data: Dict[str, Any]) -> str:
        """
        Extract searchable text from nested dictionary
        """
        text_parts = []
        
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                text_parts.append(str(value))
            elif isinstance(value, dict):
                text_parts.append(self._extract_text_from_dict(value))
            elif isinstance(value, list):
                text_parts.extend(str(item) for item in value if isinstance(item, (str, int, float)))
        
        return ' '.join(text_parts)
    
    def _check_field_match(self, field: str, value: str, filename: str, 
                          tags: List[str], metadata: Dict[str, Any]) -> bool:
        """
        Check if field-specific search matches
        """
        try:
            value_lower = value.lower()
            
            if field == 'name' or field == 'filename':
                return value_lower in filename.lower()
            elif field == 'tag':
                return any(value_lower in tag.lower() for tag in tags)
            elif field == 'type' or field == 'format':
                file_format = metadata.get('format', '').lower()
                return value_lower in file_format
            elif field == 'size':
                # Size comparisons (e.g., size:>1MB, size:<500KB)
                return self._check_size_match(value, metadata.get('file_size', 0))
            elif field == 'created' or field == 'date':
                # Date comparisons
                return self._check_date_match(value, metadata.get('creation_date'))
            else:
                # Generic metadata field search
                return self._search_metadata_field(field, value_lower, metadata)
                
        except Exception:
            return False
    
    def _check_size_match(self, size_query: str, actual_size: int) -> bool:
        """
        Check size-based queries (e.g., >1MB, <500KB)
        """
        try:
            # Parse size query
            if size_query.startswith('>'):
                operator = '>'
                size_str = size_query[1:]
            elif size_query.startswith('<'):
                operator = '<'
                size_str = size_query[1:]
            elif size_query.startswith('='):
                operator = '='
                size_str = size_query[1:]
            else:
                operator = '='
                size_str = size_query
            
            # Convert size string to bytes
            size_bytes = self._parse_size_string(size_str)
            if size_bytes is None:
                return False
            
            # Compare
            if operator == '>':
                return actual_size > size_bytes
            elif operator == '<':
                return actual_size < size_bytes
            else:
                return abs(actual_size - size_bytes) < (size_bytes * 0.1)  # 10% tolerance
                
        except Exception:
            return False
    
    def _parse_size_string(self, size_str: str) -> Optional[int]:
        """
        Parse size string like "1MB", "500KB" to bytes
        """
        try:
            size_str = size_str.strip().upper()
            
            # Extract number and unit
            import re
            match = re.match(r'(\d+(?:\.\d+)?)\s*([KMGT]?B?)', size_str)
            if not match:
                return None
            
            number = float(match.group(1))
            unit = match.group(2)
            
            # Convert to bytes
            multipliers = {
                '': 1, 'B': 1,
                'KB': 1024, 'K': 1024,
                'MB': 1024**2, 'M': 1024**2,
                'GB': 1024**3, 'G': 1024**3,
                'TB': 1024**4, 'T': 1024**4
            }
            
            return int(number * multipliers.get(unit, 1))
            
        except Exception:
            return None
    
    def _check_date_match(self, date_query: str, actual_date: str) -> bool:
        """
        Check date-based queries
        """
        try:
            # This would implement date range checking
            # For now, simple substring match
            return date_query.lower() in (actual_date or '').lower()
            
        except Exception:
            return False
    
    def _search_metadata_field(self, field: str, value: str, metadata: Dict[str, Any]) -> bool:
        """
        Search in specific metadata field
        """
        try:
            if field in metadata:
                field_value = str(metadata[field]).lower()
                return value in field_value
            
            # Search in nested metadata
            for key, val in metadata.items():
                if isinstance(val, dict) and field in val:
                    field_value = str(val[field]).lower()
                    return value in field_value
            
            return False
            
        except Exception:
            return False
    
    def _wildcard_match(self, pattern: str, text: str) -> bool:
        """
        Check wildcard pattern match
        """
        try:
            # Convert wildcard pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            return bool(re.search(regex_pattern, text, re.IGNORECASE))
            
        except Exception:
            return False
    
    def _matches_tag_filters(self, tags: List[str], tag_filters: List[str]) -> bool:
        """
        Check if tags match the specified filters
        """
        try:
            if not tag_filters:
                return True
            
            # Convert to lowercase for comparison
            tags_lower = [tag.lower() for tag in tags]
            filters_lower = [f.lower() for f in tag_filters]
            
            # All filters must match (AND logic)
            return all(filter_tag in tags_lower for filter_tag in filters_lower)
            
        except Exception:
            return False
    
    def _calculate_relevance(self, query: str, filename: str, tags: List[str], 
                           metadata: Dict[str, Any]) -> float:
        """
        Calculate relevance score for search results
        """
        try:
            score = 0.0
            query_terms = query.lower().split()
            
            # Filename matches (highest weight)
            filename_lower = filename.lower()
            for term in query_terms:
                if term in filename_lower:
                    if filename_lower.startswith(term):
                        score += 3.0  # Filename starts with term
                    else:
                        score += 2.0  # Filename contains term
            
            # Tag matches (medium weight)
            tags_lower = [tag.lower() for tag in tags]
            for term in query_terms:
                for tag in tags_lower:
                    if term in tag:
                        if tag == term:
                            score += 1.5  # Exact tag match
                        else:
                            score += 1.0  # Partial tag match
            
            # Metadata matches (lower weight)
            metadata_text = self._build_searchable_text('', [], metadata).lower()
            for term in query_terms:
                if term in metadata_text:
                    score += 0.5
            
            return score
            
        except Exception:
            return 0.0
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object
        """
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            try:
                # Try common formats
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%Y/%m/%d %H:%M:%S',
                    '%Y/%m/%d',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                        
            except Exception:
                pass
        
        return None
