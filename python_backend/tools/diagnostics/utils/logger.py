#!/usr/bin/env python3
"""
GraphiVault Diagnostic Logger
Provides consistent logging across all diagnostic scripts
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

class DiagnosticLogger:
    """
    Configurable logger for GraphiVault diagnostics
    Supports console output and file logging with different verbosity levels
    """
    
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    def __init__(self, name='graphivault_diagnostics', verbose=False, debug=False):
        """Initialize logger with configurable verbosity"""
        self.logger = logging.getLogger(name)
        self.verbose = verbose
        self.debug = debug
        
        # Set base level based on flags
        if debug:
            self.logger.setLevel(logging.DEBUG)
        elif verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)
        
        # Create console handler
        console = logging.StreamHandler()
        
        # Set format based on verbosity
        if debug:
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        else:
            formatter = logging.Formatter('[%(levelname)s] %(message)s')
            
        console.setFormatter(formatter)
        self.logger.addHandler(console)
    
    def setup_file_logging(self, log_dir='logs', filename=None):
        """Setup file logging"""
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)
            
            # Generate default filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'backend_diagnostics_{timestamp}.log'
            
            log_file = log_path / filename
            
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            
            # Always use detailed format for file logs
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.info(f"Logging to file: {log_file}")
            
            return str(log_file)
        
        except Exception as e:
            self.logger.error(f"Failed to setup file logging: {e}")
            return None
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=None):
        """Log error message with optional exception info"""
        if exc_info:
            self.logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            self.logger.error(message)
    
    def critical(self, message, exc_info=None):
        """Log critical message with optional exception info"""
        if exc_info:
            self.logger.critical(f"{message}\n{traceback.format_exc()}")
        else:
            self.logger.critical(message)
            
    def success(self, message):
        """Log success message (info level with special formatting)"""
        try:
            self.logger.info(f"✅ {message}")
        except UnicodeEncodeError:
            # Fallback for consoles that don't support Unicode
            self.logger.info(f"[PASS] {message}")
    
    def failure(self, message):
        """Log failure message (error level with special formatting)"""
        try:
            self.logger.error(f"❌ {message}")
        except UnicodeEncodeError:
            # Fallback for consoles that don't support Unicode
            self.logger.error(f"[FAIL] {message}")
    
    def section(self, title):
        """Log section header"""
        self.logger.info(f"\n{'=' * 40}\n{title}\n{'=' * 40}")
    
    def step(self, title):
        """Log step header"""
        self.logger.info(f"\n{'-' * 30}\n{title}\n{'-' * 30}")
    
    def result(self, test_name, success, message=None):
        """Log test result"""
        status = "PASS" if success else "FAIL"
        result = f"{test_name}: {status}"
        if message:
            result += f" - {message}"
            
        if success:
            self.success(result)
        else:
            self.failure(result)
        
        return success
