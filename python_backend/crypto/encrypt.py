#!/usr/bin/env python3
"""
GraphiVault Encryption Module
Provides AES-256 encryption for image files
"""

import sys
import os
import argparse
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(input_path: str, password: str) -> str:
    """Encrypt a file and return the path to the encrypted file"""
    try:
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Generate a random salt
        salt = os.urandom(16)
        
        # Derive key from password
        key = derive_key(password, salt)
        fernet = Fernet(key)
        
        # Read and encrypt the file
        with open(input_file, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = fernet.encrypt(file_data)
        
        # Create output file path
        output_path = str(input_file.with_suffix(input_file.suffix + '.encrypted'))
        
        # Write salt + encrypted data
        with open(output_path, 'wb') as f:
            f.write(salt)  # First 16 bytes are the salt
            f.write(encrypted_data)
        
        return output_path
        
    except Exception as e:
        print(f"Encryption error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python encrypt.py <file_path> <password>", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    password = sys.argv[2]
    
    encrypted_path = encrypt_file(file_path, password)
    print(encrypted_path)

if __name__ == "__main__":
    main()
