#!/usr/bin/env python3
"""
GraphiVault Session Manager
Manages user sessions, authentication state, and security policies
Implements time-bound sessions with automatic lockout protection
"""

import os
import time
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta


class SessionManager:
    """
    Session Manager - The guardian of access control
    
    Features:
    - Time-bound session management
    - Automatic session expiration
    - Failed attempt tracking and lockout
    - Session validation and renewal
    - Memory-safe session data handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize session manager"""
        self.config = {
            'timeout_minutes': 30,
            'auto_lock': True,
            'max_failed_attempts': 3,
            'lockout_duration_minutes': 15,
            'session_renewal_threshold_minutes': 5,
            **config
        }
        
        # Session state
        self._session_key = None
        self._session_start_time = None
        self._last_activity_time = None
        self._failed_attempts = 0
        self._lockout_until = None
        self._session_id = None
        
        # Security tracking
        self._password_hash = None
        self._session_validated = False
    
    def create_session(self, master_password: str) -> Optional[str]:
        """
        Create a new authenticated session
        Returns session ID if successful, None otherwise
        """
        try:
            # Check if currently locked out
            if self._is_locked_out():
                return None
            
            # Generate session ID and key
            self._session_id = self._generate_session_id()
            self._session_key = secrets.token_bytes(32)
            
            # Store password hash for validation
            self._password_hash = hashlib.sha256(master_password.encode()).hexdigest()
            
            # Set timestamps
            current_time = time.time()
            self._session_start_time = current_time
            self._last_activity_time = current_time
            
            # Mark as validated
            self._session_validated = True
            
            # Reset failed attempts on successful login
            self._failed_attempts = 0
            self._lockout_until = None
            
            return self._session_id
            
        except Exception:
            self._cleanup_session()
            return None
    
    def validate_session(self, session_id: str = None) -> bool:
        """
        Validate current session
        """
        try:
            # Check session ID if provided
            if session_id and session_id != self._session_id:
                return False
            
            # Check if session exists
            if not self._session_validated or not self._session_key:
                return False
            
            # Check if locked out
            if self._is_locked_out():
                self._cleanup_session()
                return False
            
            # Check session timeout
            if self._is_session_expired():
                self._cleanup_session()
                return False
            
            # Update last activity
            self._last_activity_time = time.time()
            
            return True
            
        except Exception:
            self._cleanup_session()
            return False
    
    def renew_session(self, master_password: str) -> bool:
        """
        Renew current session with password verification
        """
        try:
            # Validate password
            password_hash = hashlib.sha256(master_password.encode()).hexdigest()
            if password_hash != self._password_hash:
                self.record_failed_attempt()
                return False
            
            # Check if session is renewable
            if not self._session_validated:
                return False
            
            # Renew session timestamps
            current_time = time.time()
            self._last_activity_time = current_time
            
            # Optionally generate new session key for enhanced security
            if self._should_regenerate_key():
                self._session_key = secrets.token_bytes(32)
            
            return True
            
        except Exception:
            return False
    
    def destroy_session(self) -> bool:
        """
        Destroy current session and clear all data
        """
        try:
            self._cleanup_session()
            return True
        except Exception:
            return False
    
    def record_failed_attempt(self) -> None:
        """
        Record a failed authentication attempt
        """
        try:
            self._failed_attempts += 1
            
            # Check if lockout threshold reached
            if self._failed_attempts >= self.config['max_failed_attempts']:
                lockout_duration = timedelta(minutes=self.config['lockout_duration_minutes'])
                self._lockout_until = datetime.now(timezone.utc) + lockout_duration
                
                # Clean up session on lockout
                self._cleanup_session()
                
        except Exception:
            pass
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information
        """
        try:
            if not self._session_validated:
                return {'active': False}
            
            current_time = time.time()
            session_duration = current_time - (self._session_start_time or current_time)
            time_since_activity = current_time - (self._last_activity_time or current_time)
            
            timeout_seconds = self.config['timeout_minutes'] * 60
            time_remaining = max(0, timeout_seconds - time_since_activity)
            
            return {
                'active': True,
                'session_id': self._session_id,
                'duration_seconds': int(session_duration),
                'time_since_activity_seconds': int(time_since_activity),
                'time_remaining_seconds': int(time_remaining),
                'auto_lock_enabled': self.config['auto_lock'],
                'failed_attempts': self._failed_attempts,
                'locked_out': self._is_locked_out(),
                'lockout_remaining_seconds': self._get_lockout_remaining_seconds()
            }
            
        except Exception:
            return {'active': False}
    
    def is_session_active(self) -> bool:
        """
        Check if session is currently active and valid
        """
        return self.validate_session()
    
    def get_session_key(self) -> Optional[bytes]:
        """
        Get session key for cryptographic operations
        Only returns key if session is valid
        """
        if self.validate_session():
            return self._session_key
        return None
    
    def extend_session(self, minutes: int = None) -> bool:
        """
        Extend session timeout
        """
        try:
            if not self.validate_session():
                return False
            
            # Update last activity time
            self._last_activity_time = time.time()
            
            # Optionally extend beyond normal timeout
            if minutes:
                extension_seconds = minutes * 60
                self._last_activity_time += extension_seconds
            
            return True
            
        except Exception:
            return False
    
    def _generate_session_id(self) -> str:
        """
        Generate cryptographically secure session ID
        """
        # Include timestamp and random data for uniqueness
        timestamp = str(int(time.time() * 1000000))  # Microsecond precision
        random_data = secrets.token_hex(16)
        
        # Create hash of combined data
        session_data = f"{timestamp}:{random_data}".encode()
        session_hash = hashlib.sha256(session_data).hexdigest()
        
        return session_hash[:32]  # Use first 32 characters
    
    def _is_session_expired(self) -> bool:
        """
        Check if session has expired
        """
        try:
            if not self._last_activity_time:
                return True
            
            current_time = time.time()
            timeout_seconds = self.config['timeout_minutes'] * 60
            time_since_activity = current_time - self._last_activity_time
            
            return time_since_activity > timeout_seconds
            
        except Exception:
            return True
    
    def _is_locked_out(self) -> bool:
        """
        Check if currently in lockout period
        """
        try:
            if not self._lockout_until:
                return False
            
            current_time = datetime.now(timezone.utc)
            return current_time < self._lockout_until
            
        except Exception:
            return False
    
    def _get_lockout_remaining_seconds(self) -> int:
        """
        Get remaining lockout time in seconds
        """
        try:
            if not self._is_locked_out():
                return 0
            
            current_time = datetime.now(timezone.utc)
            remaining = self._lockout_until - current_time
            return max(0, int(remaining.total_seconds()))
            
        except Exception:
            return 0
    
    def _should_regenerate_key(self) -> bool:
        """
        Determine if session key should be regenerated for security
        """
        try:
            if not self._session_start_time:
                return False
            
            # Regenerate key every hour for enhanced security
            current_time = time.time()
            session_duration = current_time - self._session_start_time
            return session_duration > 3600  # 1 hour
            
        except Exception:
            return False
    
    def _cleanup_session(self) -> None:
        """
        Securely clean up session data
        """
        try:
            # Overwrite session key with random data before clearing
            if self._session_key:
                self._session_key = secrets.token_bytes(len(self._session_key))
                self._session_key = None
            
            # Overwrite password hash
            if self._password_hash:
                self._password_hash = secrets.token_hex(len(self._password_hash))
                self._password_hash = None
            
            # Clear session data
            self._session_id = None
            self._session_start_time = None
            self._last_activity_time = None
            self._session_validated = False
            
        except Exception:
            pass  # Best effort cleanup
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get security status and recommendations
        """
        try:
            status = {
                'session_active': self.is_session_active(),
                'failed_attempts': self._failed_attempts,
                'locked_out': self._is_locked_out(),
                'auto_lock_enabled': self.config['auto_lock'],
                'session_timeout_minutes': self.config['timeout_minutes'],
                'max_failed_attempts': self.config['max_failed_attempts'],
                'lockout_duration_minutes': self.config['lockout_duration_minutes'],
                'recommendations': []
            }
            
            # Generate security recommendations
            if not self.config['auto_lock']:
                status['recommendations'].append("Enable auto-lock for enhanced security")
            
            if self.config['timeout_minutes'] > 60:
                status['recommendations'].append("Consider reducing session timeout for better security")
            
            if self._failed_attempts > 0:
                status['recommendations'].append("Recent failed login attempts detected")
            
            return status
            
        except Exception:
            return {
                'session_active': False,
                'recommendations': ['Unable to determine security status']
            }
