# GraphiVault Backend Diagnostics

This directory contains diagnostic tools for the GraphiVault backend. These tools help identify and fix issues with the vault structure, crypto implementation, and other backend components.

## Tools

1. **Vault Validator**: Validates the vault structure, file formats, and crypto parameters.
2. **Backend Tester**: Tests the backend components (CryptoController, VaultManager, etc.) independently.
3. **Fix Scripts**: Fixes common issues with the backend components.

## Usage

### Using the Batch File (Windows)

Simply run `run_diagnostics.bat` and follow the prompts.

### Using the Command Line

#### Run All Diagnostics
```
python run_diagnostics.py --test-mode all --vault-path "../../test_vault" --verbose
```

#### Validate Vault Structure Only
```
python run_diagnostics.py --test-mode validate --vault-path "../../test_vault" --verbose
```

#### Run Backend Tests Only
```
python run_diagnostics.py --test-mode backend --vault-path "../../test_vault" --verbose
```

#### Fix CryptoController
```
python fix_crypto.py --fix-crypto --verbose
```

#### Create Test Vault Stubs
```
python fix_crypto.py --create-stubs --vault-path "../../test_vault" --verbose
```

## Fix for Vault Unlock Issue

The main issue causing the vault unlock to fail is in the `CryptoController.load_crypto_params()` method. 
It loads the salt from the vault.key file, but doesn't initialize the `_master_key` variable.

To fix this:

1. Run the fix script:
   ```
   python fix_crypto.py --fix-crypto
   ```

2. Create test vault stubs if needed:
   ```
   python fix_crypto.py --create-stubs
   ```

3. Run diagnostics to verify the fix:
   ```
   python run_diagnostics.py --test-mode all
   ```

## Common Issues and Solutions

### 1. Missing or Invalid Vault Files
- Run `python fix_crypto.py --create-stubs` to create valid test vault files.

### 2. CryptoController Password Verification Fails
- The fix script addresses this by patching the `load_crypto_params()` method.

### 3. Database Connection Issues
- Ensure the SQLite database exists and has the correct schema.
- Check file permissions on the database file.

### 4. Python Path Issues
- The diagnostic tools auto-adjust Python paths for imports, but if you see import errors, run from the `python_backend` directory.

## Logs

All diagnostic logs are saved in the `logs/` directory. Check these for detailed debugging information.
