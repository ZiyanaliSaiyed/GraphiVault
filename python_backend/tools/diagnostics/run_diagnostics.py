#!/usr/bin/env python3
"""
GraphiVault Backend Diagnostics
Main entry point for GraphiVault backend diagnostic tools
"""

import os
import sys
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import diagnostic tools
from utils.logger import DiagnosticLogger
from vault_validator import VaultValidator
from test_backend import BackendTester


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='GraphiVault Backend Diagnostics')
    parser.add_argument('--vault-path', type=str, default='../../test_vault',
                        help='Path to the vault directory')
    parser.add_argument('--create-missing', action='store_true',
                        help='Create missing files and directories')
    parser.add_argument('--password', type=str, default='test123',
                        help='Password to test vault unlocking')
    parser.add_argument('--test-mode', type=str, choices=['all', 'validate', 'backend'], default='all',
                        help='Test mode: validate structure only, backend only, or all tests')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--log-file', type=str,
                        help='Log file path')
    
    args = parser.parse_args()
    
    # Setup logger
    log = DiagnosticLogger(verbose=args.verbose, debug=args.debug)
    log_dir = Path(__file__).parent / 'logs'
    log.setup_file_logging(log_dir, args.log_file)
    
    # Print header
    log.section("GraphiVault Backend Diagnostics")
    log.info(f"Test mode: {args.test_mode}")
    
    # Convert relative path to absolute if needed
    vault_path = Path(args.vault_path)
    if not vault_path.is_absolute():
        script_dir = Path(__file__).parent
        vault_path = (script_dir / vault_path).resolve()
    
    log.info(f"Vault path: {vault_path}")
    
    # Run tests based on mode
    validate_success = False
    backend_success = False
    
    if args.test_mode in ['all', 'validate']:
        log.section("Vault Validation")
        validator = VaultValidator(
            vault_path=vault_path,
            log=log,
            create_missing=args.create_missing
        )
        
        validate_success = validator.run_all_checks(args.password)
        
        if not validate_success and args.test_mode == 'all':
            log.warning("Skipping backend tests due to validation failure")
            return 1
    
    if args.test_mode in ['all', 'backend']:
        log.section("Backend Tests")
        tester = BackendTester(
            vault_path=vault_path,
            log=log
        )
        
        backend_success = tester.run_all_tests(args.password)
    
    # Final summary
    log.section("Final Results")
    
    if args.test_mode in ['all', 'validate']:
        log.info(f"Validation: {'PASS' if validate_success else 'FAIL'}")
        
    if args.test_mode in ['all', 'backend']:
        log.info(f"Backend Tests: {'PASS' if backend_success else 'FAIL'}")
    
    if args.test_mode == 'all':
        overall = validate_success and backend_success
        log.result("Overall Diagnostics", overall)
        return 0 if overall else 1
    elif args.test_mode == 'validate':
        return 0 if validate_success else 1
    else:  # backend
        return 0 if backend_success else 1


if __name__ == '__main__':
    sys.exit(main())
