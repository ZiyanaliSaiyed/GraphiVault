#!/usr/bin/env python3
"""
GraphiVault Audit Logger
Privacy-first audit logging for security events and vault operations
Logs only non-identifying information for security analysis
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import threading


class AuditLogger:
    """
    Audit Logger - The watchful eye of the vault
    
    Features:
    - Privacy-first logging (no identifying information)
    - Secure log rotation and archival
    - Tamper-resistant log entries
    - Real-time security event detection
    - Local-only storage (no external transmission)
    """
    
    def __init__(self, log_file_path: str):
        """Initialize audit logger"""
        self.log_file_path = Path(log_file_path)
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.max_log_files = 5
        self.log_lock = threading.Lock()
        
        # Ensure log directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize log file if it doesn't exist
        if not self.log_file_path.exists():
            self._initialize_log_file()
    
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Log a security or operational event
        """
        try:
            with self.log_lock:
                # Create log entry
                log_entry = self._create_log_entry(event_type, event_data)
                
                # Check if log rotation is needed
                if self._should_rotate_log():
                    self._rotate_log_files()
                  # Append to log file
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                    f.flush()
                
                return True
                
        except Exception:
            return False
    
    def get_security_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get security events from the last N hours
        """
        events = []
        
        try:
            cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            
            with self.log_lock:
                if self.log_file_path.exists():
                    with open(self.log_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if (entry.get('timestamp_unix', 0) >= cutoff_time and
                                    self._is_security_event(entry.get('event_type', ''))):
                                    events.append(entry)
                            except json.JSONDecodeError:
                                continue
                
                # Also check rotated log files
                events.extend(self._get_events_from_rotated_logs(cutoff_time))
            
        except Exception:
            pass
        
        return sorted(events, key=lambda x: x.get('timestamp_unix', 0), reverse=True)
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get audit summary for the last N hours
        """
        try:
            events = self.get_all_events(hours)
            
            summary = {
                'period_hours': hours,
                'total_events': len(events),
                'event_types': {},
                'security_events': 0,
                'error_events': 0,
                'last_activity': None,
                'first_activity': None
            }
            
            for event in events:
                event_type = event.get('event_type', 'unknown')
                summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
                
                if self._is_security_event(event_type):
                    summary['security_events'] += 1
                
                if self._is_error_event(event_type):
                    summary['error_events'] += 1
                
                # Track activity timeframe
                timestamp = event.get('timestamp_unix', 0)
                if not summary['last_activity'] or timestamp > summary['last_activity']:
                    summary['last_activity'] = timestamp
                if not summary['first_activity'] or timestamp < summary['first_activity']:
                    summary['first_activity'] = timestamp
            
            return summary
            
        except Exception:
            return {'error': 'Failed to generate audit summary'}
    
    def get_all_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get all events from the last N hours
        """
        events = []
        
        try:
            cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            
            with self.log_lock:
                if self.log_file_path.exists():
                    with open(self.log_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('timestamp_unix', 0) >= cutoff_time:
                                    events.append(entry)
                            except json.JSONDecodeError:
                                continue
                
                # Also check rotated log files
                events.extend(self._get_events_from_rotated_logs(cutoff_time))
            
        except Exception:
            pass
        
        return sorted(events, key=lambda x: x.get('timestamp_unix', 0), reverse=True)
    
    def export_logs(self, output_path: str, hours: int = 24) -> bool:
        """
        Export audit logs to a file
        """
        try:
            events = self.get_all_events(hours)
            
            export_data = {
                'export_timestamp': datetime.now(timezone.utc).isoformat(),
                'period_hours': hours,
                'total_events': len(events),
                'events': events
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception:
            return False
    
    def clear_logs(self, older_than_days: int = 30) -> bool:
        """
        Clear logs older than specified days
        """
        try:
            cutoff_time = datetime.now(timezone.utc).timestamp() - (older_than_days * 24 * 3600)
            
            with self.log_lock:
                # Clear main log file
                if self.log_file_path.exists():
                    self._filter_log_file(self.log_file_path, cutoff_time)
                
                # Clear rotated log files
                for i in range(1, self.max_log_files + 1):
                    rotated_file = self.log_file_path.with_suffix(f'.{i}')
                    if rotated_file.exists():
                        # Check if entire file is old
                        if rotated_file.stat().st_mtime < cutoff_time:
                            rotated_file.unlink()
                        else:
                            self._filter_log_file(rotated_file, cutoff_time)
            
            return True
            
        except Exception:
            return False
    
    def verify_log_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of log files
        """
        integrity_report = {
            'valid': True,
            'issues': [],
            'total_entries': 0,
            'corrupted_entries': 0,
            'files_checked': 0
        }
        
        try:
            with self.log_lock:
                # Check main log file
                if self.log_file_path.exists():
                    file_report = self._verify_file_integrity(self.log_file_path)
                    integrity_report['total_entries'] += file_report['total_entries']
                    integrity_report['corrupted_entries'] += file_report['corrupted_entries']
                    integrity_report['files_checked'] += 1
                    
                    if file_report['corrupted_entries'] > 0:
                        integrity_report['valid'] = False
                        integrity_report['issues'].append(f"Main log file has {file_report['corrupted_entries']} corrupted entries")
                
                # Check rotated log files
                for i in range(1, self.max_log_files + 1):
                    rotated_file = self.log_file_path.with_suffix(f'.{i}')
                    if rotated_file.exists():
                        file_report = self._verify_file_integrity(rotated_file)
                        integrity_report['total_entries'] += file_report['total_entries']
                        integrity_report['corrupted_entries'] += file_report['corrupted_entries']
                        integrity_report['files_checked'] += 1
                        
                        if file_report['corrupted_entries'] > 0:
                            integrity_report['valid'] = False
                            integrity_report['issues'].append(f"Rotated log file {i} has {file_report['corrupted_entries']} corrupted entries")
            
        except Exception as e:
            integrity_report['valid'] = False
            integrity_report['issues'].append(f"Integrity check failed: {str(e)}")
        
        return integrity_report
    
    def _create_log_entry(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a standardized log entry
        """
        now = datetime.now(timezone.utc)
        
        # Create base log entry
        log_entry = {
            'timestamp': now.isoformat(),
            'timestamp_unix': now.timestamp(),
            'event_type': event_type,
            'session_id': self._get_session_hash(),
            'data': self._sanitize_event_data(event_data)
        }
        
        # Add integrity hash
        log_entry['integrity_hash'] = self._calculate_entry_hash(log_entry)
        
        return log_entry
    
    def _sanitize_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize event data to remove identifying information
        """
        sanitized = {}
        
        # Fields that are safe to log
        safe_fields = {
            'timestamp', 'error', 'status', 'count', 'size', 'type',
            'format', 'duration', 'result', 'method', 'version'
        }
          # Fields that should be hashed instead of logged directly
        hash_fields = {'filename', 'path', 'image_id', 'tag'}
        
        for key, value in event_data.items():
            if key in safe_fields:
                sanitized[key] = value
            elif key in hash_fields:
                # Hash identifying information
                sanitized[f'{key}_hash'] = hashlib.sha256(str(value).encode()).hexdigest()[:16]
            elif key.endswith('_count') or key.endswith('_size'):
                # Numeric data is generally safe
                sanitized[key] = value
            # Skip other potentially identifying fields
        
        return sanitized
    
    def _get_session_hash(self) -> str:
        """
        Get a non-identifying session hash
        """
        # This would get a hash of the current session ID
        # For now, return a placeholder
        return hashlib.sha256(str(os.getpid()).encode()).hexdigest()[:16]
    
    def _calculate_entry_hash(self, log_entry: Dict[str, Any]) -> str:
        """
        Calculate integrity hash for log entry
        """
        # Create hash of entry without the hash field itself
        entry_copy = log_entry.copy()
        entry_copy.pop('integrity_hash', None)
        
        entry_string = json.dumps(entry_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(entry_string.encode('utf-8')).hexdigest()[:32]
    
    def _should_rotate_log(self) -> bool:
        """
        Check if log file should be rotated
        """
        try:
            if not self.log_file_path.exists():
                return False
            
            file_size = self.log_file_path.stat().st_size
            return file_size >= self.max_log_size
            
        except Exception:
            return False
    
    def _rotate_log_files(self) -> None:
        """
        Rotate log files
        """
        try:
            # Move existing rotated files
            for i in range(self.max_log_files - 1, 0, -1):
                old_file = self.log_file_path.with_suffix(f'.{i}')
                new_file = self.log_file_path.with_suffix(f'.{i + 1}')
                
                if old_file.exists():
                    if new_file.exists():
                        new_file.unlink()
                    old_file.rename(new_file)
            
            # Move current log to .1
            if self.log_file_path.exists():
                rotated_file = self.log_file_path.with_suffix('.1')
                if rotated_file.exists():
                    rotated_file.unlink()
                self.log_file_path.rename(rotated_file)
            
            # Create new log file
            self._initialize_log_file()
            
        except Exception:
            pass  # Best effort rotation
    
    def _initialize_log_file(self) -> None:
        """
        Initialize a new log file with header
        """
        try:
            header_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'event_type': 'log_initialized',
                'version': '1.0',            'max_size_bytes': self.max_log_size
            }
            
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(header_entry, ensure_ascii=False) + '\n')
                
        except Exception:
            pass
    
    def _get_events_from_rotated_logs(self, cutoff_time: float) -> List[Dict[str, Any]]:
        """
        Get events from rotated log files
        """
        events = []
        
        try:
            for i in range(1, self.max_log_files + 1):
                rotated_file = self.log_file_path.with_suffix(f'.{i}')
                if rotated_file.exists():
                    with open(rotated_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('timestamp_unix', 0) >= cutoff_time:
                                    events.append(entry)
                            except json.JSONDecodeError:
                                continue
                                
        except Exception:
            pass
        
        return events
    
    def _filter_log_file(self, file_path: Path, cutoff_time: float) -> None:
        """
        Filter log file to remove entries older than cutoff time
        """
        try:
            temp_file = file_path.with_suffix('.tmp')
            
            with open(file_path, 'r', encoding='utf-8') as infile, \
                 open(temp_file, 'w', encoding='utf-8') as outfile:
                
                for line in infile:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('timestamp_unix', 0) >= cutoff_time:
                            outfile.write(line)
                    except json.JSONDecodeError:
                        # Keep corrupted entries for investigation
                        outfile.write(line)
            
            # Replace original file
            temp_file.replace(file_path)
            
        except Exception:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
    
    def _verify_file_integrity(self, file_path: Path) -> Dict[str, int]:
        """
        Verify integrity of a single log file
        """
        report = {'total_entries': 0, 'corrupted_entries': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    report['total_entries'] += 1
                    
                    try:
                        entry = json.loads(line.strip())
                        
                        # Verify integrity hash if present
                        if 'integrity_hash' in entry:
                            expected_hash = self._calculate_entry_hash(entry)
                            if entry['integrity_hash'] != expected_hash:
                                report['corrupted_entries'] += 1
                                
                    except json.JSONDecodeError:
                        report['corrupted_entries'] += 1
                        
        except Exception:
            pass
        
        return report
    
    def _is_security_event(self, event_type: str) -> bool:
        """
        Check if event type is security-related
        """
        security_events = {
            'vault_init_attempt', 'vault_init_error',
            'vault_unlock_attempt', 'vault_unlock_error',
            'vault_lock', 'session_expired',
            'failed_authentication', 'lockout_activated',
            'image_access_error', 'search_error'
        }
        
        return event_type in security_events
    
    def _is_error_event(self, event_type: str) -> bool:
        """
        Check if event type is error-related
        """
        return 'error' in event_type or 'failed' in event_type
