#!/usr/bin/env python3
"""
GraphiVault Decryption Module
Provides AES-256 decryption for encrypted image files
"""

import sys
import os
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

def decrypt_file(encrypted_path: str, password: str, output_path: str) -> None:
    """Decrypt an encrypted file"""
    try:
        encrypted_file = Path(encrypted_path)
        if not encrypted_file.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
        
        # Read the encrypted file
        with open(encrypted_file, 'rb') as f:
            salt = f.read(16)  # First 16 bytes are the salt
            encrypted_data = f.read()
        
        # Derive key from password and salt
        key = derive_key(password, salt)
        fernet = Fernet(key)
        
        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Write decrypted data to output file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
        
        print(f"File decrypted successfully: {output_path}")
        
    except Exception as e:
        print(f"Decryption error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Usage: python decrypt.py <encrypted_file_path> <password> <output_path>", file=sys.stderr)
        sys.exit(1)
    
    encrypted_path = sys.argv[1]
    password = sys.argv[2]
    output_path = sys.argv[3]
    
    decrypt_file(encrypted_path, password, output_path)

if __name__ == "__main__":
    main()
